# Web app static hosting: S3 + CloudFront
# Bucket is private; only CloudFront can read (OAC). Public access is via CloudFront URL only.
# Build: cd frontend/web && npm run build; upload: aws s3 sync dist/ s3://BUCKET --delete
# See docs/WEB-BACKEND-INTEGRATION-PLAN.md and docs/MVP-DEPLOY-RUNBOOK.md.
# Custom domain: set web_app_domain_name and web_app_acm_certificate_arn (cert must be in us-east-1), then add CNAME to CloudFront distribution domain.

resource "aws_s3_bucket" "web" {
  bucket = "${local.name_prefix}-web-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "${local.name_prefix}-web"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "web" {
  bucket = aws_s3_bucket.web.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "web" {
  bucket = aws_s3_bucket.web.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "web" {
  bucket = aws_s3_bucket.web.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls     = true
  restrict_public_buckets = true
}

# CloudFront OAC: only CloudFront can read from S3 (no public bucket)
resource "aws_cloudfront_origin_access_control" "web" {
  name                              = "${local.name_prefix}-web-oac"
  description                       = "OAC for web app S3 bucket"
  origin_access_control_origin_type  = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "web" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  comment             = "Emergency Medical Triage Web App"
  price_class         = "PriceClass_100" # US, Canada, Europe

  aliases = var.web_app_domain_name != "" ? [var.web_app_domain_name] : []

  origin {
    domain_name              = aws_s3_bucket.web.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.web.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.web.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.web.id}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  # SPA: 403/404 -> index.html so client router works
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = var.web_app_domain_name == "" || var.web_app_acm_certificate_arn == ""
    acm_certificate_arn            = var.web_app_domain_name != "" && var.web_app_acm_certificate_arn != "" ? var.web_app_acm_certificate_arn : null
    ssl_support_method             = var.web_app_domain_name != "" && var.web_app_acm_certificate_arn != "" ? "sni-only" : null
    minimum_protocol_version       = var.web_app_domain_name != "" && var.web_app_acm_certificate_arn != "" ? "TLSv1.2_2021" : null
  }

  tags = {
    Name        = "${local.name_prefix}-web"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Allow CloudFront OAC to read from the bucket
data "aws_iam_policy_document" "web_bucket_policy" {
  statement {
    sid    = "AllowCloudFrontServicePrincipal"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.web.arn}/*"]
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.web.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "web" {
  bucket = aws_s3_bucket.web.id
  policy = data.aws_iam_policy_document.web_bucket_policy.json
}
