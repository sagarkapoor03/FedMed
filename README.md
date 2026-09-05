# 🏥 FedMed — Privacy-Preserving Federated Learning for Healthcare

FedMed is a **privacy-preserving Federated Learning system** designed for healthcare applications.

The project allows multiple hospitals to collaboratively train a **brain tumor segmentation model using MRI scans** without sharing their raw patient data with a central server.

## 🎯 Problem

Medical data such as MRI scans and patient information is highly sensitive. Hospitals usually cannot share raw patient data because of privacy regulations such as **HIPAA and GDPR**.

Traditional machine learning requires collecting data in one central location, which creates privacy and security risks.

## 💡 Our Solution

FedMed uses **Federated Learning** to train an AI model across multiple hospitals.

Instead of sending patient data to the central server:

* Each hospital keeps its MRI data locally.
* The AI model is trained locally at each hospital.
* Only model updates are sent to the central server.
* The server combines the updates using **Federated Averaging (FedAvg)**.
* Encryption and Differential Privacy provide additional protection.

```text
                Central Server
                     │
              Global 3D U-Net
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   Hospital 1   Hospital 2   Hospital 3
   Private MRI  Private MRI  Private MRI
        │            │            │
        ↓            ↓            ↓
    Local Train   Local Train   Local Train
        │            │            │
        └────────────┼────────────┘
                     ↓
              Secure Updates
                     ↓
                FedAvg
                     ↓
              Global Model
```

## 🧠 AI Model

FedMed uses a **3D U-Net** architecture for brain tumor segmentation.

The model takes a 3D MRI scan as input and predicts the region containing the tumor.

```text
MRI Scan
   ↓
3D U-Net
   ↓
Tumor Segmentation
   ↓
Segmentation Mask
```

## 🔐 Privacy & Security

The project includes multiple privacy and security techniques:

* **Federated Learning** — raw medical data stays at the hospital.
* **Homomorphic Encryption** — model updates can be encrypted before transmission.
* **Differential Privacy** — controlled noise is added to reduce privacy risks.
* **TLS/gRPC** — secure communication between server and hospital nodes.

## 🛠️ Technology Stack

| Component            | Technology |
| -------------------- | ---------- |
| Programming Language | Python     |
| Deep Learning        | PyTorch    |
| Medical AI           | MONAI      |
| Federated Learning   | Flower     |
| Encryption           | TenSEAL    |
| Communication        | gRPC + TLS |
| Frontend             | React      |
| Visualization        | Recharts   |
| Model                | 3D U-Net   |

## 📊 Dataset

The project will use a publicly available brain MRI dataset such as the **BraTS (Brain Tumor Segmentation)** dataset.

The dataset will be divided among three simulated hospital nodes.

> ⚠️ Raw medical datasets will not be uploaded to this GitHub repository.

## 🏥 Simulated Hospital Nodes

FedMed will simulate three independent hospitals:

```text
Hospital 1 → Local MRI Dataset → Local Training
Hospital 2 → Local MRI Dataset → Local Training
Hospital 3 → Local MRI Dataset → Local Training
```

Each hospital trains the model independently and sends only the required model updates to the central server.

## 📅 Development Plan

### Week 1 — Centralized Baseline & Setup

* Set up PyTorch and MONAI
* Prepare MRI dataset
* Implement 3D U-Net
* Train centralized baseline model
* Set up Flower
* Create three simulated hospital nodes

### Week 2 — Federated Learning

* Partition dataset across hospitals
* Implement local training
* Implement FedAvg
* Connect server and clients
* Add secure gRPC communication
* Handle offline hospital nodes

### Week 3 — Privacy

* Integrate TenSEAL
* Encrypt model updates
* Perform secure aggregation
* Add live training metrics

### Week 4 — Final System

* Add Differential Privacy
* Build React dashboard
* Display training curves
* Display Dice Score and Loss
* Display MRI segmentation masks
* Compare centralized and federated performance

## 📈 Expected Results

The final system aims to demonstrate that:

1. Multiple hospitals can collaboratively train an AI model.
2. Raw MRI data remains within each hospital.
3. Federated training can achieve performance close to centralized training.
4. Model updates can be protected using encryption and privacy techniques.
5. Training progress can be monitored through a web dashboard.

## 🚀 Project Goal

The goal of FedMed is to demonstrate how **Federated Learning and Privacy-Preserving Machine Learning** can be applied to healthcare while reducing the need to share sensitive patient data.

## 👨‍💻 Project Status

🚧 **Currently under development**

### Future Improvements

* Support for real hospital deployments
* More advanced secure aggregation
* Improved 3D medical segmentation models
* Additional privacy-preserving techniques
* Cloud-based deployment
* Support for multiple medical imaging datasets

---

### 📜 License

This project is developed for **educational and research purposes**.
