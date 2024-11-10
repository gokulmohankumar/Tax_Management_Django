# Tax Management System

A web-based application for managing and calculating taxes efficiently, built with Django. This project supports two types of users: Admin and Individual User. Users can register, verify their email, and update their tax information, while admins have access to manage users and oversee the tax management system.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)

## Features
- **User Registration and Verification**: Secure registration process with email verification.
- **Admin Dashboard**: Admins can manage users and view tax-related data.
- **Tax Calculation**: Implements both old and new tax regimes based on the latest tax policies.
- **Profile Management**: Users can update their profile information and income details.
- **Secure Authentication**: User authentication for access control.
- **Cloud Storage Integration**: Uses Cloudinary for media storage.

## Installation

### Prerequisites
- Python 3.x
- Django 4.x
- Git
- Virtual Environment (optional but recommended)

### Steps
1. Clone the repository
   ```bash
   git clone https://github.com/gokulmohankumar/Tax_Management_Django.git
   cd Tax_Management_Django

2. Set up a virtual environment
   - On MacOS/Linux:
     ```bash
     python -m venv env
     source env/bin/activate
     ```
   - On Windows:
     ```bash
     env\Scripts\activate
     ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   Create a `.env` file in the project root with the following variables:
   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=your_database_url
   CLOUDINARY_URL=your_cloudinary_url
   ```

5. Apply migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Run the development server
   ```bash
   python manage.py runserver
   ```

7. Access the application
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
