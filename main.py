#!/usr/bin/env python3
"""
Hackathon Sponsorship Outreach Automation Script

This script automates sponsorship email outreach for college hackathons using Gmail SMTP.
It reads sponsor data from CSV, sends personalized emails, and implements strict
anti-duplication, rate limiting, and resume safety features.

Author: Ayan Gattani
"""

import csv
import os
import time
import smtplib
import logging
import random
import configparser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Tuple
import sys


class SponsorshipOutreachAutomation:
    """Main class for automating hackathon sponsorship outreach."""
    
    def __init__(self, config_file: str = "config/config.ini"):
        """
        Initialize the sponsorship outreach automation system.
        
        Args:
            config_file: Path to the configuration file containing SMTP credentials
        """
        self.config_file = config_file
        self.csv_file = "sponsors.csv"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_user = None
        self.smtp_password = None
        self.sender_name = None
        
        # Rate limiting settings
        self.min_delay = 5  # Minimum delay between emails (seconds)
        self.max_delay = 13  # Maximum delay between emails (seconds)
        self.emails_per_batch = 40  # Number of emails before cooldown
        self.cooldown_duration = 35 * 60  # Cooldown duration in seconds (35 minutes)
        
        # Email counters
        self.emails_sent = 0
        self.batch_start_time = None
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.load_configuration()
        
        # Load email templates
        self.email_templates = self.load_email_templates()
        
    def setup_logging(self):
        """Configure logging for the script."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_configuration(self):
        """
        Load SMTP configuration from config file or environment variables.
        
        Raises:
            ValueError: If required configuration is missing
        """
        # Try to load from config file first
        if os.path.exists(self.config_file):
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            if 'SMTP' in config:
                self.smtp_user = config['SMTP'].get('user', None)
                self.smtp_password = config['SMTP'].get('password', None)
                self.sender_name = config['SMTP'].get('sender_name', None)
        
        # Override with environment variables if available
        if os.environ.get('SMTP_USER'):
            self.smtp_user = os.environ['SMTP_USER']
        if os.environ.get('SMTP_PASSWORD'):
            self.smtp_password = os.environ['SMTP_PASSWORD']
        if os.environ.get('SENDER_NAME'):
            self.sender_name = os.environ['SENDER_NAME']
            
        # Validate required configuration
        if not self.smtp_user:
            raise ValueError("SMTP user not configured. Set SMTP_USER environment variable or configure in config.ini")
        if not self.smtp_password:
            raise ValueError("SMTP password not configured. Set SMTP_PASSWORD environment variable or configure in config.ini")
        if not self.sender_name:
            self.sender_name = "RoboVITics"
            
        self.logger.info(f"Configuration loaded successfully for user: {self.smtp_user}")
        
    def load_email_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Load email templates for different sponsor categories.
        
        Returns:
            Dictionary containing email templates for each category
        """
        templates = {}
        
        # Template directory
        template_dir = "email_templates"
        
        # Define template files for each category
        template_files = {
            'Mechanical': {'txt': 'mechanical_template.txt', 'html': 'mechanical_template.html'},
            'CS': {'txt': 'cs_template.txt', 'html': 'cs_template.html'},
            'General': {'txt': 'general_template.txt', 'html': 'general_template.html'}
        }
        
        for category, files in template_files.items():
            template_data = {}
            
            # Load text template
            txt_file = os.path.join(template_dir, files['txt'])
            if os.path.exists(txt_file):
                with open(txt_file, 'r', encoding='utf-8') as f:
                    template_data['text'] = f.read()
                self.logger.info(f"Loaded text template for {category} category")
            
            # Load HTML template if available
            if 'html' in files:
                html_file = os.path.join(template_dir, files['html'])
                if os.path.exists(html_file):
                    with open(html_file, 'r', encoding='utf-8') as f:
                        template_data['html'] = f.read()
                    self.logger.info(f"Loaded HTML template for {category} category")
            
            if template_data:
                templates[category] = template_data
            else:
                self.logger.warning(f"No template files found for {category} category")
                # Create a default template if no files exist
                templates[category] = {
                    'text': self.get_default_template(category)
                }
                
        return templates
        
    def get_default_template(self, category: str) -> str:
        """
        Generate a default email template for a category.
        
        Args:
            category: The sponsor category (Mechanical, CS, General)
            
        Returns:
            Default email template string
        """
        event_name = "Vortex360 '26" if category == "Mechanical" else "Equinox '26"
        
        if category == "Mechanical":
            subject_line = f"Partnership Opportunity: {event_name} Hackathon Sponsorship"
            focus_area = "CAD, mechanical design, and engineering innovation"
        elif category == "CS":
            subject_line = f"Partnership Opportunity: {event_name} Hackathon Sponsorship"
            focus_area = "software development, AI/ML, and digital innovation"
        else:
            subject_line = f"Partnership Opportunity: {event_name} Hackathon Sponsorship"
            focus_area = "technology innovation and community engagement"
            
        template = f"""Subject: {subject_line}

Dear {{poc_name}},

I hope this email finds you well. My name is {self.sender_name}, and I'm reaching out regarding an exciting sponsorship opportunity with {event_name}, our upcoming hackathon focused on {focus_area}.

Event Overview:
- Event Name: {event_name}
- Focus Area: {focus_area}
- Participants: 200+ talented students and professionals
- Duration: 48-hour intensive coding and innovation event

Why Partner with Us:
- Direct access to emerging talent in technology
- Brand visibility among next-generation innovators
- Opportunity to showcase your company's cutting-edge solutions
- Networking with industry leaders and academic institutions

We believe in flexible sponsorship packages that align with your marketing objectives and budget. Our team is open to discussing various partnership levels and benefits that would be most valuable for {{company_name}}.

We would love to schedule a brief call to discuss how {{company_name}} can be part of this exciting event. Are you available for a 15-minute conversation this week to explore this opportunity?

Best regards,
{self.sender_name}
{event_name} Sponsorship Team
Email: {self.smtp_user}
"""
        return template
        
    def get_category_info(self, category: str) -> Tuple[str, str]:
        """
        Get event name and brochure filename for a category.
        
        Args:
            category: The sponsor category
            
        Returns:
            Tuple of (event_name, brochure_filename)
        """
        if category == "Mechanical":
            return "Vortex360 '26", "Vortex360 '26.pdf"
        else:
            return "Equinox '26", "Equinox '26.pdf"
            
    def get_attachment_filename(self, category: str) -> Optional[str]:
        """
        Get the filename for the category-specific brochure.
        
        Args:
            category: The sponsor category
            
        Returns:
            Filename of the brochure or None if not found
        """
        _, brochure_filename = self.get_category_info(category)
        filepath = os.path.join("brochures", brochure_filename)
        return filepath if os.path.exists(filepath) else None
        
    def read_sponsors_csv(self) -> List[Dict[str, str]]:
        """
        Read sponsor data from CSV file.
        
        Returns:
            List of sponsor dictionaries
        """
        sponsors = []
        
        if not os.path.exists(self.csv_file):
            self.logger.error(f"CSV file not found: {self.csv_file}")
            return sponsors
            
        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, 1):
                    # Validate required fields
                    if not all(key in row for key in ['Company Name', 'POC Name', 'Email Address']):
                        self.logger.warning(f"Row {row_num}: Missing required fields, skipping")
                        continue
                        
                    # Clean and normalize data
                    sponsor = {
                        'Company Name': row['Company Name'].strip() if row.get('Company Name') else '',
                        'POC Name': row['POC Name'].strip() if row.get('POC Name') else '',
                        'Email Address': row['Email Address'].strip().lower() if row.get('Email Address') else '',
                        'Category': self.normalize_category(row.get('Category', '').strip() if row.get('Category') else ''),
                        'Status': row.get('Status', 'Not Sent').strip() if row.get('Status') else 'Not Sent',
                        'Sent Timestamp': row.get('Sent Timestamp', '').strip() if row.get('Sent Timestamp') else ''
                    }
                    
                    # Skip if status is already "Sent"
                    if sponsor['Status'] == 'Sent':
                        self.logger.info(f"Skipping {sponsor['Company Name']} - already sent")
                        continue
                        
                    # Validate email format (basic)
                    if '@' not in sponsor['Email Address']:
                        self.logger.warning(f"Row {row_num}: Invalid email format, skipping")
                        continue
                        
                    sponsors.append(sponsor)
                    
            self.logger.info(f"Loaded {len(sponsors)} sponsors from CSV")
            
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            
        return sponsors
        
    def normalize_category(self, category: str) -> str:
        """
        Normalize category values according to business rules.
        
        Args:
            category: Raw category from CSV
            
        Returns:
            Normalized category
        """
        category = category.strip()
        if category in ['Mechanical', 'CS']:
            return category
        else:
            return 'General'
            
    def create_email_message(self, sponsor: Dict[str, str]) -> MIMEMultipart:
        """
        Create email message for a sponsor.
        
        Args:
            sponsor: Sponsor dictionary containing recipient information
            
        Returns:
            MIMEMultipart email message
        """
        category = sponsor['Category']
        event_name, _ = self.get_category_info(category)
        
        # Get template content
        template_data = self.email_templates.get(category, {})
        
        # Determine if we should use HTML or text
        html_content = template_data.get('html')
        text_content = template_data.get('text')
        
        if html_content:
            # Use HTML template
            email_content = html_content.format(
                company_name=sponsor['Company Name'],
                poc_name=sponsor['POC Name'],
                event_name=event_name,
                sender_name=self.sender_name,
                sender_email=self.smtp_user
            )
            
            # Create message with HTML content
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.sender_name} <{self.smtp_user}>"
            message['To'] = sponsor['Email Address']
            message['Cc'] = "robovitics@vit.ac.in"
            message['Subject'] = f"Vortex 360 Sponsorship 2026 – VIT Vellore" if category == "Mechanical" else f"Equinox Sponsorship 2026 – VIT Vellore"
            
            # Attach HTML part
            html_part = MIMEText(email_content, 'html', 'utf-8')
            message.attach(html_part)
            
        else:
            # Use text template (existing logic)
            if not text_content:
                text_content = self.get_default_template(category)
                
            email_content = text_content.format(
                company_name=sponsor['Company Name'],
                poc_name=sponsor['POC Name'],
                event_name=event_name,
                sender_name=self.sender_name,
                sender_email=self.smtp_user
            )
            
            # Create message with text content
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.sender_name} <{self.smtp_user}>"
            message['To'] = sponsor['Email Address']
            message['Cc'] = "robovitics@vit.ac.in"
            message['Subject'] = f"Vortex 360 Sponsorship 2026 – VIT Vellore" if category == "Mechanical" else f"Equinox Sponsorship 2026 – VIT Vellore"
            
            # Add HTML content (converted from text)
            html_content_converted = self.convert_to_html(email_content)
            html_part = MIMEText(html_content_converted, 'html', 'utf-8')
            message.attach(html_part)
        
        # Add attachment if available
        attachment_file = self.get_attachment_filename(category)
        if attachment_file and os.path.exists(attachment_file):
            self.attach_file(message, attachment_file)
            
        return message
        
    def convert_to_html(self, text_content: str) -> str:
        """
        Convert plain text email content to HTML.
        
        Args:
            text_content: Plain text email content
            
        Returns:
            HTML formatted email content
        """
        # Simple text to HTML conversion
        html_content = text_content.replace('\n\n', '</p><p>')
        html_content = html_content.replace('\n', '<br>')
        html_content = f'<p>{html_content}</p>'
        
        # Add some basic styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                p {{ margin-bottom: 1em; }}
                strong {{ color: #2c3e50; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return styled_html
        
    def attach_file(self, message: MIMEMultipart, filepath: str):
        """
        Attach a file to the email message.
        
        Args:
            message: MIMEMultipart message object
            filepath: Path to file to attach
        """
        try:
            with open(filepath, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(filepath)}'
            )
            
            message.attach(part)
            self.logger.info(f"Attached file: {os.path.basename(filepath)}")
            
        except Exception as e:
            self.logger.error(f"Error attaching file {filepath}: {e}")
            
    def send_email(self, message: MIMEMultipart, sponsor: Dict[str, str]) -> bool:
        """
        Send email to sponsor via SMTP.
        
        Args:
            message: Email message to send
            sponsor: Sponsor information for logging
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            
            # Send email
            text = message.as_string()
            all_recipients = [message['To']]
            if message['Cc']:
                all_recipients.append(message['Cc'])
            server.sendmail(self.smtp_user, all_recipients, text)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {sponsor['Email Address']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {sponsor['Email Address']}: {e}")
            return False
            
    def apply_rate_limiting(self):
        """Apply rate limiting delays between emails."""
        # Check if we need a cooldown
        if self.emails_sent > 0 and self.emails_sent % self.emails_per_batch == 0:
            self.logger.info(f"Reached {self.emails_per_batch} emails. Starting cooldown for {self.cooldown_duration // 60} minutes.")
            self.logger.info(f"Cooldown will end at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Save batch start time for resume
            if self.batch_start_time:
                elapsed_time = time.time() - self.batch_start_time
                remaining_cooldown = max(0, self.cooldown_duration - elapsed_time)
                
                if remaining_cooldown > 0:
                    self.logger.info(f"Resuming after {remaining_cooldown / 60:.1f} minutes of remaining cooldown...")
                    time.sleep(remaining_cooldown)
            else:
                time.sleep(self.cooldown_duration)
                
            self.batch_start_time = time.time()
            
        # Apply random delay between emails
        delay = random.randint(self.min_delay, self.max_delay)
        self.logger.info(f"Waiting {delay} seconds before next email...")
        time.sleep(delay)
        
    def update_csv_status(self, sponsor: Dict[str, str], success: bool):
        """
        Update CSV file with send status.
        
        Args:
            sponsor: Sponsor information
            success: Whether the email was sent successfully
        """
        if not success:
            return  # Don't update status if send failed
            
        try:
            # Read current CSV data
            rows = []
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                
                for row in reader:
                    # Update the specific row
                    if (row['Email Address'].strip().lower() == sponsor['Email Address'] and
                        row['Company Name'].strip() == sponsor['Company Name']):
                        row['Status'] = 'Sent'
                        row['Sent Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                    rows.append(row)
            
            # Write updated data back to CSV
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
            self.logger.info(f"Updated CSV status for {sponsor['Company Name']}")
            
        except Exception as e:
            self.logger.error(f"Error updating CSV file: {e}")
            
    def run(self):
        """
        Main execution method for the sponsorship outreach automation.
        """
        self.logger.info("Starting Hackathon Sponsorship Outreach Automation")
        self.logger.info("=" * 60)
        
        # Load sponsors from CSV
        sponsors = self.read_sponsors_csv()
        
        if not sponsors:
            self.logger.error("No valid sponsors found to process")
            return
            
        self.logger.info(f"Processing {len(sponsors)} sponsors")
        self.logger.info("=" * 60)
        
        # Process each sponsor
        for i, sponsor in enumerate(sponsors, 1):
            try:
                self.logger.info(f"Processing sponsor {i}/{len(sponsors)}: {sponsor['Company Name']}")
                
                # Create email message
                message = self.create_email_message(sponsor)
                
                # Send email
                success = self.send_email(message, sponsor)
                
                # Update CSV status if successful
                if success:
                    self.update_csv_status(sponsor, success)
                    self.emails_sent += 1
                    
                    # Apply rate limiting
                    self.apply_rate_limiting()
                else:
                    self.logger.warning(f"Skipping rate limiting for failed email to {sponsor['Company Name']}")
                    
            except Exception as e:
                self.logger.error(f"Error processing sponsor {sponsor['Company Name']}: {e}")
                continue
                
        self.logger.info("=" * 60)
        self.logger.info(f"Automation completed. {self.emails_sent} emails sent successfully.")
        self.logger.info("=" * 60)


def main():
    """Main entry point for the script."""
    try:
        # Initialize and run the automation
        automation = SponsorshipOutreachAutomation()
        automation.run()
        
    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        print("Note: The script will resume from unsent emails when restarted.")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Please check the configuration and try again.")


if __name__ == "__main__":
    main()
