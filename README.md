# Booksy Lite

#### Video Demo: https://www.youtube.com/watch?v=CbDJNkZpKjo


#### Description:

Booksy Lite is a web application designed to solve the problem of inefficient appointment management for small service businesses. The idea for this project came from my personal observation of how many barbers manage appointments, especially during busy periods such as holidays and special occasions. Many of them still depend on WhatsApp messages or even handwritten notebooks to organize their appointments. While these methods may work for a small number of customers, they become inefficient during peak times because they can easily create confusion, missed appointments, overlapping bookings, and difficulty tracking availability.

The goal of Booksy Lite is to provide a structured appointment management system that allows businesses to organize their services, providers, and schedules while giving customers an easier way to book appointments.

This project was developed as my final project for CS50. It was built using Flask, Python, SQLite, HTML, and Jinja templates. Through this project, I applied concepts learned throughout the course, including backend development, database design, SQL queries, authentication, and connecting different parts of a web application together.

The application is based on three main roles: owners, providers, and customers. Customers are users who want to book appointments. Providers are users who perform services and have their own working schedules. Owners are responsible for managing businesses, services, and providers connected to their business.

The booking process in Booksy Lite follows a structured flow. A customer first searches for a business and selects the desired business. After that, the customer views the services offered by that business and chooses the service they want. The application then displays the providers who are capable of performing that service. After selecting a provider, the customer chooses a date and views the available time slots based on the provider's working hours, the duration of the selected service, and existing appointments. Finally, the customer selects an available time and creates the appointment.

The most important design decision in this project was the database design. I consider building this database structure one of the most valuable parts of the project because I designed it myself with scalability in mind rather than only creating something that works for the current version.

Instead of creating a simple database where each service belongs directly to one provider, I designed a more flexible structure. Providers and services are separated entities, and the relationship between them is handled through a separate relationship table. This creates a many-to-many relationship where one provider can offer multiple services, and one service can be performed by multiple providers.

This decision prevents unnecessary limitations in the future. For example, if a barber shop has several employees who can all perform the same service, the database can represent this naturally. At the same time, one provider can specialize in several different services without duplicating data.

Another important design choice was separating owners, providers, and customers into different entities instead of putting all information into one large user table. This separation makes the database clearer and allows each role to have its own specific information and responsibilities. However, I also designed the structure in a way that allows future expansion, where one user could potentially have multiple roles instead of being restricted to only one role. For example, a person could be both an owner and a provider in the same system.

The database structure contains several main tables. The users table stores common account information such as usernames, emails, and password hashes. Separate tables represent owners, providers, and customers. The business table connects businesses with their owners. The service table stores available services and their durations. The service_providing table manages the relationship between services and providers. Finally, the appointment table stores customer bookings and connects customers, services, and providers together.

Another important decision was how to represent time. Instead of storing working hours as normal time strings, I converted times into minutes. This makes it easier to calculate available slots, compare appointment durations, and detect conflicts between appointments.

The main files in this project are:

`app.py`:
This file contains the Flask application logic. It handles routes, authentication, user management, business management, service management, provider management, appointment creation, and all communication with the database.

`schema.sql`:
This file contains the complete SQLite database structure. It defines all tables, primary keys, and foreign key relationships used by the application.

`templates/`:
This folder contains the HTML templates used by Flask. These pages display dynamic information using Jinja, including businesses, services, providers, available times, and appointments.

`static/`:
This folder contains CSS files used to style and design the user interface.

Building Booksy Lite was an important learning experience because it required more than simply writing code. The most challenging and rewarding part was designing a database structure that is organized, flexible, and capable of supporting future improvements. Creating a database with clear relationships between different entities taught me the importance of planning before implementation.

I am especially proud of the database design because it transformed the project from a simple appointment application into a structure that can grow into a larger system. The separation of roles, the many-to-many relationship between services and providers, and the focus on scalability allowed me to build a foundation that can support additional features in the future.

This project represents my understanding of how real-world applications are designed: not only by making features work, but by creating a strong structure that allows the application to evolve.
