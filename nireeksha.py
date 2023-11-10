import streamlit as st
import sqlite3
from PIL import Image
import pillow_heif
import io

# Install pillow_heif if not already installed using:
# pip install pillow_heif
st.set_page_config(page_title="Actress Portfolio", layout="wide", page_icon=":star:")
# Initialize connection
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return sqlite3.connect('portfolio.db', check_same_thread=False)

conn = init_connection()

# Create table function
def create_table():
    conn.execute('''CREATE TABLE IF NOT EXISTS image_store
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  image BLOB NOT NULL);''')
    conn.commit()

create_table() # Create the table if it doesn't exist

# Function to insert image into the database
def insert_image(name, img):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    conn.execute('INSERT INTO image_store (name, image) VALUES (?, ?)', (name, img_byte_arr))
    conn.commit()

# Function to convert HEIC to JPEG and return as Image object
def convert_heic_to_jpeg(uploaded_file):
    heif_file = pillow_heif.read_heif(uploaded_file)
    image = Image.frombytes(
        heif_file.mode, 
        heif_file.size, 
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    return image

# Function to load images from the database
def load_images_from_db():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM image_store")
    data = cursor.fetchall()
    images = []
    for row in data:
        name, image_data = row[1], row[2]
        image = Image.open(io.BytesIO(image_data))
        images.append((name, image))
    return images
    
def save_heic_file(uploaded_file):
    # Convert the PIL Image object to a byte array and save to the database
    try:
        # Read the HEIC file
        heif_file = pillow_heif.open_heif(uploaded_file.getvalue())
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride)
        # Insert image into the database after converting to JPEG
        insert_image(uploaded_file.name, image)
        st.success(f"{uploaded_file.name} converted and saved to database.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
   
def style_sidebar():
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background-color: #f1f3f6;
            border-right: 2px solid #e0e0e0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

style_sidebar()    

# Main app function
def main():
    st.title('Actress Portfolio')

    # Sidebar for navigation
    st.sidebar.title('Navigation')
    page = st.sidebar.radio("Go to", ['Home', 'About', 'Gallery', 'Filmography', 'Contact'])

    # Home Page
    if page == 'Home':
        st.header('Welcome to My Portfolio')
        st.write("I'm [Actress Name], a professional actress with a passion for storytelling.")

    # About Page
    elif page == 'About':
        st.header('About Me')
        st.write('Here you can put the biography of the actress or any other details you want to share.')

    # Gallery Page
    elif page == 'Gallery':
        st.header('Gallery')
        uploaded_files = st.file_uploader("Upload Images", type=["heic", "jpg", "jpeg", "png"], accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Check if uploaded file is HEIC format
                if uploaded_file.type == "image/heif":
                    save_heic_file(uploaded_file)  # Handle HEIC files
                else:
                    # Handle other image formats
                    try:
                        image = Image.open(uploaded_file)
                        insert_image(uploaded_file.name, image)
                        st.success(f"{uploaded_file.name} saved to database.")
                    except Exception as e:
                        st.error(f"An error occurred while saving {uploaded_file.name}: {e}")

        if st.button('Show Images'):
            images = load_images_from_db()
            cols = st.columns(3)  # Three columns for the gallery
            for idx, (name, image) in enumerate(images):
                with cols[idx % 3]:
                    st.image(image, caption=name, use_column_width=True)
    # Filmography Page
    elif page == 'Filmography':
        st.header('Filmography')
        # You can use a simple list
        filmography_list = [
            'Film Title 1 - Role - Year',
            'Film Title 2 - Role - Year',
            # Add more films here
        ]
        for film in filmography_list:
            st.write("- ", film)

    # Contact Page
    elif page == 'Contact':
        st.header('Contact Information')
        st.write('For booking and inquiries, please reach out through the following channels:')
        st.write('Email: [actress_email@example.com]')
        st.write('Phone: [(555) 123-4567]')
        st.write('Agent: [Agent Name] - [agent_contact@example.com]')

if __name__ == "__main__":
    main()

