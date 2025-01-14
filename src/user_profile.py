import os
import streamlit as st
from spanner_utils import hash_password, fetch_user_details, update_user_details
from email_utils import validate_email, send_email


def profile_page():
    """Render the Profile Page."""
    # Add a header banner with a gradient background
    st.markdown(
        """
        <style>
        .header-banner {
            background: linear-gradient(to right, #4CAF50, #2E8B57);
            color: white;
            padding: 15px;
            text-align: center;
            border-radius: 5px;
            font-family: Arial, sans-serif;
            font-size: 24px;
            margin-bottom: 20px;
        }
        </style>
        <div class="header-banner">
            Let's explore your profile, Bhaskar!
        </div>
        """,
        unsafe_allow_html=True,
    )

    user_id = st.session_state.get("user_id")

    if not user_id:
        st.warning("Please log in to view your profile.")
        return

    # Fetch user details
    user_details = fetch_user_details(user_id)

    if not user_details:
        st.error("Unable to fetch user details. Please try again.")
        return

    # Extract user details
    first_name, last_name, email, profile_picture_url = user_details

    # Layout for profile picture and user details
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Profile Picture")
        uploaded_file = st.file_uploader("Upload New Profile Picture", type=["jpg", "png"])
        if uploaded_file:
            # Ensure the `user_uploads` directory exists
            upload_directory = "user_uploads"
            if not os.path.exists(upload_directory):
                os.makedirs(upload_directory)

            # Define the file path for the uploaded picture
            profile_picture_path = os.path.join(upload_directory, f"{user_id}_{uploaded_file.name}")
            with open(profile_picture_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            profile_picture_url = profile_picture_path  # Update profile picture URL
            st.image(profile_picture_path, use_column_width=True, caption="Uploaded Profile Picture")
            st.success("Profile picture updated! Click 'Save Changes' to store it.")

        elif profile_picture_url:
            st.image(profile_picture_url, use_column_width=True, caption="Your Profile Picture")
        else:
            st.image("https://via.placeholder.com/150", use_column_width=True, caption="Default Profile Picture")
            st.warning("No profile picture found. Please upload one.")

    with col2:
        st.subheader("Profile Information")
        first_name = st.text_input("First Name", value=first_name)
        last_name = st.text_input("Last Name", value=last_name)
        email = st.text_input("Email", value=email)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Password update section
        st.subheader("Change Password")
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")

        # Save Changes Button
        if st.button("Save Changes"):
            if new_password and new_password != confirm_password:
                st.error("Passwords do not match.")
            elif not validate_email(email):
                st.error("Invalid email format.")
            else:
                try:
                    update_user_details(
                        user_id=user_id,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=new_password if new_password else None,
                        profile_picture_url=profile_picture_url,
                    )
                    st.success("Profile updated successfully!")
                except Exception as e:
                    st.error(f"Error updating profile: {e}")
