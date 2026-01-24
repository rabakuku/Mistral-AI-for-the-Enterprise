# The Provider block connects Terraform to your Google Cloud account.
# It tells Terraform which project and region to use based on your variables.
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# 1. Instance Scheduling Policy: Your "Auto-Stop" money saver! 💰
# This automatically shuts down the VM at 11 PM EST daily to ensure you never pay for idle time overnight.
resource "google_compute_resource_policy" "daily_stop" {
  name   = "daily-stop-policy"
  region = var.region

  instance_schedule_policy {
    vm_stop_schedule {
      schedule = "0 4 * * *" # 4:00 AM UTC = 11:00 PM EST
    }
    time_zone = "UTC"
  }
}

# 2. Firewall Rule: The "Admin Gate." 🛡️
# This opens the specific ports needed for SSH, vLLM, and Ollama, but ONLY to your specific IP address for maximum security.
resource "google_compute_firewall" "allow_my_ip" {
  name    = "allow-admin-access"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "8000", "11434", "8501"]
  }

  source_ranges = [var.my_ip]
  description   = "Allow SSH, vLLM, and Ollama from admin IP"
}

# 3. Firewall Rule: Secure Tunneling (IAP). 🚇
# This allows Google's Identity-Aware Proxy to manage SSH connections securely without exposing the VM to the open internet.
resource "google_compute_firewall" "allow_iap_ssh" {
  name    = "allow-iap-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]
  description   = "Allow Identity-Aware Proxy for secure SSH"
}

# 4. The Sovereign AI Engine: The actual server. 🧠
# This provisions the NVIDIA L4 GPU, 100GB of high-speed SSD storage, and the Debian OS tailored for AI workloads.
resource "google_compute_instance" "ai_engine" {
  name         = "sovereign-ai-engine"
  machine_type = "g2-standard-4"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 100
      type  = "pd-ssd"
    }
    auto_delete = true
  }

  # This block physically attaches the NVIDIA L4 GPU to your machine.
  guest_accelerator {
    type  = "nvidia-l4"
    count = 1
  }

  scheduling {
    on_host_maintenance = "TERMINATE" # GPUs require a hard termination during maintenance rather than a live migration.
    automatic_restart   = true
    provisioning_model  = "STANDARD"
  }

  network_interface {
    network = "default"
    access_config {
      network_tier = "PREMIUM"
    }
  }

  # This attaches the automatic shutdown policy we created in section #1.
  resource_policies = [google_compute_resource_policy.daily_stop.id]

  metadata = {
    enable-osconfig       = "TRUE"
    install-nvidia-driver = "True" # This tells GCP to automatically install the GPU drivers for us!
  }
}
