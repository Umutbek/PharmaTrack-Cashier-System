# PharmaTrack Cashier System

## Overview
PharmaTrack Cashier System is a comprehensive solution for managing pharmacy inventory and sales. The system allows cashiers to scan drugs, track inventory, and order drugs from the depot efficiently. It ensures accurate sales transactions and real-time stock updates, making pharmacy management seamless and effective.

## Features
### Sales Management
- **Drug Scanning:** Cashiers can scan drugs to automatically display the drug name, price, and amount.
- **Quantity Management:** If the same drug is scanned multiple times, the system increments the amount accordingly.
- **Stock Updates:** Sold items are automatically removed from the system, and stock levels are updated in real-time.

### Inventory Tracking
- **Stock Monitoring:** Keep track of the remaining stock for all pharmacy items.
- **Order Management:** Easily order drugs from the depot through the system.

## Installation
### Prerequisites
- Docker
- Docker Compose

### Docker Setup
1. Clone the repository:
    ```sh
    git clone https://github.com/Umutbek/PharmaTrack-Cashier-System.git
    cd PharmaTrack-Cashier-System
    ```
2. Build and start the containers:
    ```sh
    docker-compose up --build
    ```
3. Apply migrations:
    ```sh
    docker-compose exec web python manage.py migrate
    ```
4. Create a superuser to access the admin interface:
    ```sh
    docker-compose exec web python manage.py createsuperuser
    ```
5. Access the application at `http://localhost:8000`.

## Usage
- **Drug Scanning:** Scan drugs at the cashier to automatically manage sales and inventory.
- **Stock Management:** Monitor and track stock levels, and order drugs from the depot as needed.

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License
This project is licensed under the MIT License.

## Contact
For any questions or suggestions, please contact:
- **Umutbek Abdimanan uulu:** abdimananuuluumutbe@cityuniversity.edu

---
