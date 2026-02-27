from sqlalchemy import asc, desc
from utils.constants import *
from supabase import create_client, Client
import mimetypes,os,uuid,datetime,re, json, io
from utils.constants import *
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
import aiosmtplib

def unique_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('upload/', datetime.datetime.now().strftime('%Y/%m/%d'), filename)

def validate_fields(data):
    errors = {}
    for key,val in data.items():
        if val is None or val == "":
            errors[key] = f"Required field"
    return errors

def months_between(date1, date2):
    # Ensure date1 is before date2
    if date1 > date2:
        date1, date2 = date2, date1
    num_months = (date2.year - date1.year) * 12 + date2.month - date1.month
    num_months+=1
    return num_months

def generate_order_number(order_id):
    date_str = datetime.datetime.now().strftime("%Y%m%d")  # e.g. 20250718
    expense_num = f"ORD-{date_str}-{str(order_id).zfill(5)}"
    return expense_num

def generate_business_id(business_id,TYPE):
    return f"{TYPE}{str(business_id).zfill(6)}"


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

async def upload_file(file):
    file_url = None
    if file:
        try:
            file_ext = os.path.splitext(file.filename)[1]
            file_name = f"{uuid.uuid4()}{file_ext}"
            mime_type, _ = mimetypes.guess_type(file_name)

            file_bytes = file.read()
            header = {
                "content-type": mime_type,
                "x-upsert": "true"  # overwrite if exists
            }

            supabase: Client = create_client(SUPABASE_ENDIPONT, SUPABASE_KEY)
            response = await supabase.storage.from_(SUPABASE_BUCKET).upload(f"invoice/{file_name}", file_bytes, header)
            file_url = await supabase.storage.from_(SUPABASE_BUCKET).get_public_url(f"invoice/{file_name}")
            return file_url
        except:
            pass
        return file_url

def execute_query(db,execution_type,obj):
    if execution_type == 'create':
        db.add(obj)
        db.commit()
        db.refresh(obj)
        msg = 'Record created'
        return {
                "msg": msg,
                "data": obj
            }
    elif execution_type == 'update':
        db.commit()
        db.refresh(obj)
        msg = 'Record updated'
        return {
                "msg": msg,
                "data": obj
            }
    elif execution_type == 'delete':
        db.delete(obj)
        db.commit()
        msg = 'Record deleted'
        return {
                "msg": msg,
            }

def get_records(
    model_name,
    obj,
    page: int = None,
    order_by: str = None,
    order_dir: str = None
):
    total = obj.count()

    # Safe ordering
    if order_by and hasattr(model_name, order_by):
        column = getattr(model_name, order_by)
        obj = obj.order_by(asc(column) if order_dir and order_dir.lower() == "asc" else desc(column))

    # Pagination
    if page is not None:
        obj = obj.offset((page - 1) * int(PAGE_SIZE)).limit(int(PAGE_SIZE))

    data = obj.all()  # always fetch list

    return {
        "msg": "List of records",
        "total": total,
        "page": page,
        "page_size": PAGE_SIZE,
        "data": data
    }



def get_all_records(
        model_name,
        obj
        ):
    if hasattr(model_name):
        total = obj.count()
        obj.all()
        return {
        "msg": "List of records",
        "total": total,
        "data": obj
    }

# Load Jinja2 template environment
env = Environment(loader=FileSystemLoader("email_templates/"))

async def send_html_email(to_email: str, subject: str, template_name: str, context: dict):
    # Render the HTML template with context
    template = env.get_template(template_name)
    html_content = template.render(context)

    # Create email message
    message = EmailMessage()
    message["From"] = "youremail@example.com"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content("This is an HTML email.")  # Fallback
    message.add_alternative(html_content, subtype="html")

    # Send the email using SMTP
    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",      # or your SMTP server
        port=587,
        username="naiyeraazam@gmail.com",
        password="czvlofjdkdkcvjuf",
        start_tls=True,
    )
