# This identifies your GCP Project. Replace the default with your ID from Phase 1.
variable "project_id" {
  description = "The GCP Project ID"
  type        = string
  default     = "YOUR_PROJECT_ID"
}

# This sets the general location of your data center.
variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-east1"
}

# This sets the specific data center hall (Zone) within your region.
variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-east1-b"
}

# Your public IP address. This is the "Lock" on the door that only your computer has the key to.
variable "my_ip" {
  description = "Your public IP address in CIDR format (e.g., 1.2.3.4/32)"
  type        = string
  default     = "0.0.0.0/0" # REPLACE THIS WITH YOUR ACTUAL IP
}

# The G2 series is optimized for high-performance NVIDIA GPUs.
variable "machine_type" {
  description = "The machine type for the instance"
  type        = string
  default     = "g2-standard-4"
}

