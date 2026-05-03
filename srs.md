## Pharmacy POS System (Pakistan)

**Software Requirements Specification (SRS) + Roadmap**
**Tech Stack:** Python + PyQt (Desktop UI) + SQLite (Local DB)

---

# 1. Introduction

## 1.1 Purpose

Define requirements for a desktop Pharmacy POS system tailored to Pakistani pharmacies. The system will handle sales, inventory, medicine tracking, reporting, and compliance with local practices.

## 1.2 Scope

The system will:

* Manage medicine inventory (batch, expiry, supplier)
* Process retail sales (POS billing)
* Handle customer and supplier records
* Generate reports (sales, stock, profit)
* Support offline-first usage (SQLite)

## 1.3 Users

* Pharmacy Owner
* Sales Staff (Cashier)
* Admin

---

# 2. Overall Description

## 2.1 Product Perspective

Standalone desktop application:

* Runs offline
* Lightweight and fast
* Optional future sync with cloud

## 2.2 Key Features

* POS Billing (barcode/manual)
* Inventory with expiry alerts
* Batch tracking (important for pharma)
* Supplier & purchase management
* Reports & analytics
* Role-based access

## 2.3 Constraints

* Must run on low-spec PCs (2–4 GB RAM)
* No internet dependency
* SQLite DB (single-user optimized)

---

# 3. Functional Requirements

## 3.1 Authentication

* Login system
* Roles:

  * Admin
  * Cashier

**Features**

* Secure login
* Session handling

---

## 3.2 POS Billing Module

### Features

* Add medicines via:

  * Barcode scan
  * Search by name
* Auto price fetch
* Quantity input
* Discount (per item / total)
* Tax handling (GST optional)
* Multiple payment modes:

  * Cash
  * Card
  * Easypaisa/JazzCash (manual entry)

### Output

* Printable receipt

---

## 3.3 Inventory Management

### Features

* Add/Edit/Delete medicines
* Fields:

  * Name
  * Generic name
  * Category
  * Purchase price
  * Sale price
  * Batch number
  * Expiry date
  * Quantity
  * Supplier

### Alerts

* Low stock alert
* Expiry alert (30/60/90 days configurable)

---

## 3.4 Purchase Management

### Features

* Add purchase invoices
* Link supplier
* Batch-wise entry
* Auto stock update

---

## 3.5 Supplier Management

### Features

* Add/Edit suppliers
* Track purchase history
* Outstanding balances

---

## 3.6 Customer Management (Optional Phase 2)

### Features

* Customer records
* Purchase history
* Credit handling

---

## 3.7 Reporting Module

### Reports

* Daily/Monthly sales
* Profit report
* Stock report
* Expiry report
* Purchase report

### Export

* PDF
* CSV

---

## 3.8 Backup & Restore

* Local DB backup
* Restore functionality

---

# 4. Non-Functional Requirements

## Performance

* Load time < 2 seconds
* POS transaction < 1 second

## Usability

* Simple UI (non-technical users)
* Urdu/English support (optional)

## Reliability

* No data loss on crash
* Auto-save transactions

## Security

* Password hashing
* Role-based access

---

# 5. System Architecture

## 5.1 Architecture Pattern

* MVC (Model-View-Controller)

## 5.2 Components

* UI Layer → PyQt
* Logic Layer → Python services
* Data Layer → SQLite

---

# 6. Database Design (SQLite)

## Tables

### Users

* id
* username
* password_hash
* role

### Medicines

* id
* name
* generic_name
* category
* sale_price

### Inventory

* id
* medicine_id
* batch_no
* expiry_date
* quantity
* purchase_price
* supplier_id

### Sales

* id
* date
* total_amount
* discount
* payment_method

### SaleItems

* id
* sale_id
* medicine_id
* quantity
* price

### Suppliers

* id
* name
* phone
* address

### Purchases

* id
* supplier_id
* date
* total_amount

### PurchaseItems

* id
* purchase_id
* medicine_id
* batch_no
* expiry_date
* quantity
* purchase_price

---

# 7. UI Modules (PyQt Screens)

* Login Screen
* Dashboard
* POS Screen
* Inventory Screen
* Purchase Screen
* Supplier Screen
* Reports Screen
* Settings

---

# 8. Roadmap (Development Plan)

## Phase 1: Foundation (Week 1–2)

* Project setup
* SQLite schema
* Basic PyQt layout
* Authentication system

## Phase 2: Core POS (Week 3–4)

* POS billing screen
* Sales + SaleItems logic
* Receipt generation

## Phase 3: Inventory (Week 5–6)

* Medicine management
* Batch + expiry system
* Stock updates

## Phase 4: Purchases (Week 7)

* Supplier module
* Purchase entry
* Stock integration

## Phase 5: Reports (Week 8)

* Sales reports
* Stock reports
* Expiry alerts

## Phase 6: Optimization (Week 9)

* Performance tuning
* UI improvements
* Error handling

## Phase 7: Deployment (Week 10)

* EXE build (PyInstaller)
* Installer creation
* User testing

---

# 9. Future Enhancements

* Cloud sync (multi-branch)
* Barcode integration hardware
* WhatsApp invoice sharing
* Mobile app integration
* FBR integration (if required)

---

# 10. Risks

* Data corruption (SQLite misuse)
* Poor UI adoption
* Hardware compatibility issues

---

# 11. Success Metrics

* POS transaction speed < 1 sec
* Zero data loss incidents
* User adoption within 1 week

---

If needed, next step can be:

* Folder structure + clean architecture
* PyQt UI wireframes
* Full database SQL script
* Starter codebase (enterprise structure)
