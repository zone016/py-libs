import argparse
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from socket import inet_aton
from typing import Tuple

from printer.console import err, inf, sanitize, suc


def send_email(
    smtp_server: str,
    port: int,
    sender: str,
    recipient: str,
    message: str,
    subject: str = 'Message Sent via CLI',
) -> None:
    """
    Sends an email using an SMTP server without authentication.

    :param smtp_server: str, the address of the SMTP server.
    :param port: int, the port of the SMTP server.
    :param sender: str, the email address of the sender.
    :param recipient: str, the email address of the recipient.
    :param message: str, the message to be sent.
    :param subject: str, the subject of the email.
    """
    try:
        # Create the message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Send the email
        with smtplib.SMTP(smtp_server, port) as server:
            server.sendmail(sender, recipient, msg.as_string())
            suc('Email sent successfully!')
    except Exception as e:
        err(f'Failed to send email: [b]{e}[/b].')


def is_valid_email(email: str) -> bool:
    """
    Validates an email address based on a simple regex pattern.

    :param email: str, the email address to validate.
    :return: bool, True if the email address is valid, False otherwise.
    """
    # Simple regex for validating an email address (basic validation)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_smtp_server(server: str) -> Tuple[bool, str]:
    """
    Validates an SMTP server address (hostname or IP).

    :param server: str, the server address to validate.
    :return: Tuple[bool, str], True with 'hostname' or 'IP' if valid,
             False with reason otherwise.
    """
    try:
        inet_aton(server)
        return True, 'IP'
    except OSError:
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', server):
            return True, 'hostname'
        else:
            return (
                False,
                'Invalid SMTP server address. '
                'Please provide a valid hostname or IP address.',
            )


def validate_arguments(args: argparse.Namespace) -> None:
    """
    Validates command line arguments.

    :param args: The parsed command line arguments.
    """
    valid_server, server_type = is_valid_smtp_server(args.smtp_server)
    if not valid_server:
        err(server_type)
        exit(1)

    if not is_valid_email(args.sender):
        err(
            f'The [b]{sanitize(args.sender)}[/b] is an invalid '
            f'sender email address.'
        )
        exit(1)

    if not is_valid_email(args.recipient):
        err(
            f'The [b]{sanitize(args.recipient)}[/b] is an invalid '
            f'recipient email address.'
        )
        exit(1)


def main() -> None:
    """
    Parses command line arguments and sends the email after validation.
    """
    parser = argparse.ArgumentParser(
        description='Sends emails using an SMTP '
        'server without authentication.',
        epilog='Example: mailer smtp.host.net sender@host.com '
        'recipient@host.com "message" --subject "pwned" --port 1337',
    )
    parser.add_argument('smtp_server', type=str, help='SMTP server address')
    parser.add_argument('sender', type=str, help='Sender email address')
    parser.add_argument('recipient', type=str, help='Recipient email address')
    parser.add_argument('message', type=str, help='Message to be sent')
    parser.add_argument(
        '--subject',
        type=str,
        default='Message Sent via CLI',
        help='Email subject (default: "Message Sent via CLI")',
    )
    parser.add_argument(
        '--port', type=int, default=25, help='SMTP server port (default: 25)'
    )

    args = parser.parse_args()
    inf('Validating arguments...')

    validate_arguments(args)
    inf('Sending email...')

    send_email(
        args.smtp_server,
        args.port,
        args.sender,
        args.recipient,
        args.message,
        args.subject,
    )


if __name__ == '__main__':
    main()
