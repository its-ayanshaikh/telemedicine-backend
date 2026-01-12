from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from streamlit import user


def get_default_password(user):
    if user.role == "doctor":
        first = (user.first_name or "").lower()
        last = (user.last_name or "").lower()
        return f"{first}{last}@123"

    elif user.role == "hospital":
        name = (user.hospital_name or "").replace(" ", "").lower()
        return f"{name}@123"

    return None

def get_approval_email_template(user):
    """Email template for approved users"""
    # Get user details with fallbacks
    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""
    name = f"{first_name} {last_name}".strip() if (first_name or last_name) else user.username
    role = user.role.replace("-", " ").title() if user.role else "User"
    # Generate default password
    default_password = get_default_password(user)
    username = user.username
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <!-- Header -->
            <tr>
                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 700;">
                        🏥 SwasthLink
                    </h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">
                        Your Health, Our Priority
                    </p>
                </td>
            </tr>
            
            <!-- Success Icon -->
            <tr>
                <td style="padding: 40px 30px 20px 30px; text-align: center;">
                    <div style="width: 80px; height: 80px; background-color: #10b981; border-radius: 50%; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 40px; line-height: 80px;">✓</span>
                    </div>
                </td>
            </tr>
            
            <!-- Content -->
            <tr>
                <td style="padding: 20px 30px 40px 30px; text-align: center;">
                    <h2 style="color: #1f2937; margin: 0 0 15px 0; font-size: 24px;">
                        Congratulations, {name}! 🎉
                    </h2>
                    <p style="color: #6b7280; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                        Your registration as a <strong style="color: #667eea;">{role}</strong> on SwasthLink has been 
                        <span style="color: #10b981; font-weight: 600;">approved</span> by our admin team.
                    </p>
                    
                    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 20px; margin: 25px 0;">
                        <p style="color: #166534; margin: 0; font-size: 15px;">
                            ✅ You now have full access to all SwasthLink features and services.
                        </p>
                    </div>
                    
                    <!-- Login Credentials Box -->
                    <div style="background-color: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 12px; padding: 25px; margin: 25px 0; text-align: left;">
                        <h3 style="color: #0369a1; margin: 0 0 15px 0; font-size: 18px; text-align: center;">
                            🔐 Your Login Credentials
                        </h3>
                        <table width="100%" cellpadding="8" cellspacing="0" style="font-size: 15px;">
                            <tr>
                                <td style="color: #64748b; width: 40%;">Username:</td>
                                <td style="color: #1e293b; font-weight: 600;">{username}</td>
                            </tr>
                            <tr>
                                <td style="color: #64748b;">Password:</td>
                                <td style="color: #1e293b; font-weight: 600; font-family: monospace; background-color: #e0f2fe; padding: 8px 12px; border-radius: 6px;">{default_password}</td>
                            </tr>
                        </table>
                        <p style="color: #dc2626; margin: 15px 0 0 0; font-size: 13px; text-align: center;">
                            ⚠️ Please change your password after first login for security.
                        </p>
                    </div>
                    
                    <!-- CTA Button -->
                    <a href="#" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 15px 40px; border-radius: 8px; font-weight: 600; font-size: 16px; margin-top: 20px;">
                        Login to Dashboard
                    </a>
                </td>
            </tr>
            
            <!-- Features -->
            <tr>
                <td style="padding: 30px; background-color: #f9fafb;">
                    <h3 style="color: #374151; margin: 0 0 20px 0; font-size: 18px; text-align: center;">
                        What you can do now:
                    </h3>
                    <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="padding: 10px; text-align: center;">
                                <div style="background: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                    <span style="font-size: 30px;">📅</span>
                                    <p style="color: #4b5563; margin: 10px 0 0 0; font-size: 14px;">Manage Appointments</p>
                                </div>
                            </td>
                            <td style="padding: 10px; text-align: center;">
                                <div style="background: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                    <span style="font-size: 30px;">💬</span>
                                    <p style="color: #4b5563; margin: 10px 0 0 0; font-size: 14px;">Video Consultations</p>
                                </div>
                            </td>
                            <td style="padding: 10px; text-align: center;">
                                <div style="background: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                    <span style="font-size: 30px;">📋</span>
                                    <p style="color: #4b5563; margin: 10px 0 0 0; font-size: 14px;">Health Records</p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            
            <!-- Footer -->
            <tr>
                <td style="background-color: #1f2937; padding: 30px; text-align: center;">
                    <p style="color: #9ca3af; margin: 0 0 10px 0; font-size: 14px;">
                        Need help? Contact us at <a href="mailto:support@swasthlink.com" style="color: #667eea;">support@swasthlink.com</a>
                    </p>
                    <p style="color: #6b7280; margin: 0; font-size: 12px;">
                        © 2024 SwasthLink. All rights reserved.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def get_rejection_email_template(user):
    """Email template for rejected users"""
    name = user.first_name or user.username
    role = user.role.replace("-", " ").title() if user.role else "User"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <!-- Header -->
            <tr>
                <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 700;">
                        🏥 SwasthLink
                    </h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 14px;">
                        Your Health, Our Priority
                    </p>
                </td>
            </tr>
            
            <!-- Status Icon -->
            <tr>
                <td style="padding: 40px 30px 20px 30px; text-align: center;">
                    <div style="width: 80px; height: 80px; background-color: #ef4444; border-radius: 50%; margin: 0 auto;">
                        <span style="font-size: 40px; line-height: 80px; color: white;">✕</span>
                    </div>
                </td>
            </tr>
            
            <!-- Content -->
            <tr>
                <td style="padding: 20px 30px 40px 30px; text-align: center;">
                    <h2 style="color: #1f2937; margin: 0 0 15px 0; font-size: 24px;">
                        Registration Update
                    </h2>
                    <p style="color: #6b7280; font-size: 16px; line-height: 1.6; margin: 0 0 25px 0;">
                        Dear <strong>{name}</strong>,<br><br>
                        We regret to inform you that your registration as a <strong style="color: #667eea;">{role}</strong> 
                        on SwasthLink could not be approved at this time.
                    </p>
                    
                    <div style="background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 12px; padding: 20px; margin: 25px 0;">
                        <p style="color: #991b1b; margin: 0; font-size: 15px;">
                            <strong>Possible Reasons:</strong>
                        </p>
                        <ul style="color: #7f1d1d; text-align: left; margin: 15px 0 0 0; padding-left: 20px; font-size: 14px; line-height: 1.8;">
                            <li>Incomplete or incorrect documentation</li>
                            <li>Unable to verify credentials</li>
                            <li>Missing required information</li>
                        </ul>
                    </div>
                    
                    <div style="background-color: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 20px; margin: 25px 0;">
                        <p style="color: #92400e; margin: 0; font-size: 15px;">
                            💡 <strong>What can you do?</strong><br><br>
                            Please review your submitted documents and re-apply with correct information. 
                            If you believe this is an error, please contact our support team.
                        </p>
                    </div>
                    
                    <!-- CTA Button -->
                    <a href="mailto:support@swasthlink.com" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 15px 40px; border-radius: 8px; font-weight: 600; font-size: 16px; margin-top: 20px;">
                        Contact Support
                    </a>
                </td>
            </tr>
            
            <!-- Footer -->
            <tr>
                <td style="background-color: #1f2937; padding: 30px; text-align: center;">
                    <p style="color: #9ca3af; margin: 0 0 10px 0; font-size: 14px;">
                        Need help? Contact us at <a href="mailto:support@swasthlink.com" style="color: #667eea;">support@swasthlink.com</a>
                    </p>
                    <p style="color: #6b7280; margin: 0; font-size: 12px;">
                        © 2024 SwasthLink. All rights reserved.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def send_status_email(user, status):
    """
    Send email based on user status change
    status: 'approved' or 'rejected'
    """
    if not user.email:
        print(f"No email found for user {user.username}")
        return False
    
    try:
        if status == "approved":
            subject = "🎉 SwasthLink - Your Registration is Approved!"
            html_content = get_approval_email_template(user)
        elif status == "rejected":
            subject = "SwasthLink - Registration Update"
            html_content = get_rejection_email_template(user)
        else:
            print(f"Unknown status: {status}")
            return False
        
        message = Mail(
            from_email='outwavesolutions@gmail.com',  # Update with your verified sender email
            to_emails=user.email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"Email sent to {user.email} - Status: {response.status_code}")
        return response.status_code == 202
        
    except Exception as e:
        print(f"Error sending email to {user.email}: {str(e)}")
        return False
