provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# 1. Declare the VPC Network
# This ensures a private, isolated environment for your Sovereign AI engine.
resource "google_compute_network" "vpc_network" {
  name                    = "sovereign-ai-vpc"
  auto_create_subnetworks = true
}

# 2. Instance Scheduling Policy (Stop at 11 PM EST / 04:00 UTC)
# Crucial for maintaining the "Sustainability" part of your ROI model.
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

# 3. Firewall Rule: Allow Your IP (SSH, vLLM, Ollama)
resource "google_compute_firewall" "allow_my_ip" {
  name    = "allow-admin-access"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22", "8000", "11434"]
  }

  source_ranges = [var.my_ip]
  description   = "Allow SSH, vLLM, and Ollama from admin IP"
}

# 4. Firewall Rule: Allow Google IAP for SSH
# Provides a secure fallback for SSH without exposing port 22 to the whole internet.
resource "google_compute_firewall" "allow_iap_ssh" {
  name    = "allow-iap-ssh"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]
  description   = "Allow Identity-Aware Proxy for secure SSH"
}

# 5. The Sovereign AI Engine Instance
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

  guest_accelerator {
    type  = "nvidia-l4"
    count = 1
  }

  # Necessary when using GPUs
  scheduling {
    on_host_maintenance = "TERMINATE"
    automatic_restart   = true
    provisioning_model  = "STANDARD"
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {
      network_tier = "PREMIUM"
    }
  }

  # Attach the scheduling policy
  resource_policies = [google_compute_resource_policy.daily_stop.id]

  metadata = {
    enable-osconfig       = "TRUE"
    install-nvidia-driver = "True"
  }
}
