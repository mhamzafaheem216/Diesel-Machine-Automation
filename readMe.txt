

Database Information:

1. Create Tables:
    
    -- Table: audit_log
        CREATE TABLE audit_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            raw_data VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

    -- Table: transaction_log
        CREATE TABLE transaction_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            card_number VARCHAR(50) NOT NULL,
            fuel_info DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

    -- Table: card_balances
        CREATE TABLE card_balances (
            id INT AUTO_INCREMENT PRIMARY KEY,
            card_number VARCHAR(50) NOT NULL,
            fuel_balance DECIMAL(10,2) NOT NULL,
            card_type VARCHAR(50),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );


    