variable "project_id" {
  description = "The GCP Project ID"
  type        = string
  default     = "My First Project"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "my_ip" {
  description = "Your public IP address in CIDR format (e.g., 1.2.3.4/32)"
  type        = string
  default     = "100.14.223.170/32" # REPLACE THIS WITH YOUR ACTUAL IP
}

variable "machine_type" {
  description = "The machine type for the instance"
  type        = string
  default     = "g2-standard-4"
}
