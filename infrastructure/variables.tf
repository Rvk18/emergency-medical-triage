variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "emergency-medical-triage"
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "db_username" {
  description = "Master username for Aurora"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Master password for Aurora"
  type        = string
  sensitive   = true
}

# Bastion (optional - for SSH tunnel to Aurora)
variable "enable_bastion" {
  description = "Create bastion host for SSH tunnel to Aurora"
  type        = bool
  default     = false
}

variable "bastion_ssh_public_key" {
  description = "SSH public key for bastion (contents of ~/.ssh/id_rsa.pub)"
  type        = string
  default     = ""
}

variable "bastion_allowed_cidr" {
  description = "CIDR allowed to SSH to bastion (e.g. YOUR_IP/32)"
  type        = string
  default     = ""
}

# Bedrock Agent (leave empty to use Converse API fallback)
variable "bedrock_agent_id" {
  description = "Bedrock Agent ID for triage (empty = use Converse API)"
  type        = string
  default     = ""
}

variable "bedrock_agent_alias_id" {
  description = "Bedrock Agent Alias ID"
  type        = string
  default     = "TSTALIASID"
}

variable "bedrock_model_id" {
  description = "Bedrock model for Converse fallback (when agent not configured)"
  type        = string
  default     = "us.anthropic.claude-3-5-sonnet-v2:0"
}

# Hospital Matcher (leave empty to use Converse API; migrating to AgentCore)
variable "bedrock_hospital_matcher_agent_id" {
  description = "Bedrock Agent ID for Hospital Matcher (empty = use Converse API)"
  type        = string
  default     = ""
}

variable "bedrock_hospital_matcher_agent_alias_id" {
  description = "Bedrock Agent Alias ID for Hospital Matcher"
  type        = string
  default     = "TSTALIASID"
}

# AgentCore (when use_agentcore=true, Hospital Matcher uses AgentCore Runtime)
variable "use_agentcore" {
  description = "Use AgentCore Runtime for Hospital Matcher (requires agent_runtime_arn)"
  type        = bool
  default     = false
}

variable "agent_runtime_arn" {
  description = "AgentCore Runtime ARN for Hospital Matcher (from agentcore deploy)"
  type        = string
  default     = ""
}

# Eka Care API (for Eka MCP - Indian drugs, treatment protocols)
variable "eka_api_key" {
  description = "Eka Care API key (from console.eka.care). Stored in Secrets Manager."
  type        = string
  default     = ""
  sensitive   = true
}
