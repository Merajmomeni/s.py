from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import socket
import requests
import whois

# توکن ربات تلگرام شما
TOKEN = "8066385909:AAGsXAU9k_SCLjTKyp1KfI2IuxUo6TyOh9I"

def get_ip(domain):
    """تبدیل دامنه به آی‌پی"""
    try:
        return socket.gethostbyname(domain)
    except Exception as e:
        return f"آدرس آی‌پی پیدا نشد. خطا: {e}"

def check_wordpress(domain):
    """بررسی وجود وردپرس روی دامنه"""
    try:
        response = requests.get(f"http://{domain}/wp-login.php", timeout=5)
        if response.status_code == 200:
            return "این سایت از وردپرس استفاده می‌کند."
        else:
            return "این سایت از وردپرس استفاده نمی‌کند."
    except requests.exceptions.RequestException as e:
        return f"عدم دسترسی به سرور برای بررسی وردپرس. خطا: {e}"

def get_domain_info(domain):
    """جمع‌آوری اطلاعات دامنه"""
    try:
        w = whois.whois(domain)
        info = f"""
        **اطلاعات دامنه:**
        - نام دامنه: {w.domain_name}
        - نام سرور: {w.name_servers}
        - تاریخ ثبت: {w.creation_date}
        - تاریخ انقضا: {w.expiration_date}
        """
        return info
    except Exception as e:
        return f"اطلاعات دامنه یافت نشد. خطا: {e}"

def scan_ports(domain, ports):
    """اسکن پورت‌ها برای دامنه خاص"""
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)  # زمان تایم‌اوت برای اتصال
                result = s.connect_ex((domain, port))
                if result == 0:
                    open_ports.append(port)
        except socket.error:
            continue
    return open_ports

async def get_all_info(update: Update, context: CallbackContext):
    """هندلر برای دریافت اطلاعات کامل سرور و دامنه"""
    if len(context.args) == 0:
        await update.message.reply_text("لطفاً یک دامنه وارد کنید. مثال: /get example.com")
        return
    
    domain = context.args[0]
    ip = get_ip(domain)
    wordpress_status = check_wordpress(domain)
    domain_info = get_domain_info(domain)

    # اسکن پورت‌های باز
    ports_to_scan = [80, 443, 8080, 22, 21]  # پورت‌هایی که می‌خواهیم اسکن کنیم
    open_ports = scan_ports(domain, ports_to_scan)

    response = f"""
    **اطلاعات کامل دامنه {domain}:**
    - آی‌پی: {ip}
    - وردپرس: {wordpress_status}
    {domain_info}
    - پورت‌های باز: {', '.join(map(str, open_ports)) if open_ports else 'هیچ پورت بازی پیدا نشد.'}
    """
    await update.message.reply_text(response, parse_mode="Markdown")

def main():
    # ساخت اپلیکیشن تلگرام
    application = Application.builder().token(TOKEN).build()

    # هندلر برای دستور /get
    application.add_handler(CommandHandler("get", get_all_info))

    # شروع ربات
    application.run_polling()

if __name__ == '__main__':
    main()
