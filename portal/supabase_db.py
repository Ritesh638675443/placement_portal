from supabase import create_client
import bcrypt
import re
import uuid
SUPABASE_URL = "https://cmfttqqtqeddzqjalvxb.supabase.co"

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtZnR0cXF0cWVkZHpxamFsdnhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk4MTY5MjEsImV4cCI6MjA5NTM5MjkyMX0.SkdAAJ9thKe-_rk0TFnargcwgS2hA9V89kG2I7msyJU"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Register User ────────────────────────────────────
def register_user(reg_no, name, password, email="", domain=""):

    if len(reg_no) != 10 or not reg_no.isdigit():
        return False, "Registration number must be exactly 10 digits."

    if len(name.strip()) < 2:
        return False, "Please enter your full name."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    try:

        existing = (
            supabase.table("users")
            .select("*")
            .eq("reg_no", reg_no)
            .execute()
        )

        if existing.data:
            return False, "This registration number is already registered."

        pwd_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        data = {
            "reg_no": reg_no,
            "name": name.strip(),
            "email": email.strip(),
            "password_hash": pwd_hash,
            "domain": domain
        }

        supabase.table("users").insert(data).execute()
        return True, "Account created successfully!"

    except Exception as e:
        return False, str(e)


# ── Login User ───────────────────────────────────────
def login_user(reg_no, password):

    if reg_no.strip().lower() == "admin" and password == "admin123":

        return True, "Admin login successful!", {
            "reg_no": "admin",
            "name": "Admin",
            "email": "admin@ceg.ac.in",
            "domain": "All",
            "is_admin": True,
            "id": 0
        }

    try:

        response = (
            supabase.table("users")
            .select("*")
            .eq("reg_no", reg_no)
            .execute()
        )

        if not response.data:
            return False, "No account found.", None

        user = response.data[0]

        if bcrypt.checkpw(
            password.encode(),
            user["password_hash"].encode()
        ):

            user["is_admin"] = False

            return True, "Login successful!", user

        return False, "Incorrect password.", None

    except Exception as e:
        return False, str(e), None


# ── Updates ──────────────────────────────────────────
def post_update(message):

    try:

        data = {
            "message": message,
            "author": "Admin"
        }

        supabase.table("updates").insert(data).execute()
        return True

    except Exception:
        return False


def get_updates():

    try:

        response = (
            supabase.table("updates")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception:
        return []


def delete_update(update_id):

    try:

        (
            supabase.table("updates")
            .delete()
            .eq("id", update_id)
            .execute()
        )

        return True

    except Exception:
        return False


def extract_links(text):

    return re.findall(r'https?://[^\s]+', text)

# ─────────────────────────────────────────
# Community Posts
# ─────────────────────────────────────────

def upload_community_image(file):

    try:

        filename = f"{uuid.uuid4()}_{file.name}"

        print("FILE:", filename)

        result = supabase.storage.from_("community-images").upload(
            filename,
            file.getvalue()
        )

        print("UPLOAD RESULT:", result)

        url = supabase.storage.from_(
            "community-images"
        ).get_public_url(filename)

        print("URL:", url)

        return url

    except Exception as e:

        print("UPLOAD ERROR:", e)

        return None


def create_community_post(user_id, author_name, content, linkedin_url=None):

    try:

        data = {
            "user_id": user_id,
            "author_name": author_name,
            "content": content,
            "linkedin_url": linkedin_url
        }

        supabase.table(
            "community_posts"
        ).insert(data).execute()

        return True

    except Exception as e:
        print(e)
        return False


def get_community_posts():

    try:

        response = (
            supabase.table("community_posts")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data

    except Exception as e:
        print(e)
        return []
        
def delete_community_post(post_id):

    try:

        (
            supabase.table("community_posts")
            .delete()
            .eq("id", post_id)
            .execute()
        )

        return True

    except Exception as e:

        print(e)

        return False
