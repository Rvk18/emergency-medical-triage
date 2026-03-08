# S3 bucket for Android APK download. Served publicly via CloudFront (OAC); S3 is private.
# Upload: aws s3 cp app.apk s3://BUCKET/apk/MedTriage.apk --content-type application/vnd.android.package-archive
# See docs/MVP-DEPLOY-RUNBOOK.md for build + upload steps.

resource "aws_s3_bucket" "apk" {
  bucket = "${local.name_prefix}-apk-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "${local.name_prefix}-apk"
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "apk" {
  bucket = aws_s3_bucket.apk.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "apk" {
  bucket = aws_s3_bucket.apk.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 is private; only CloudFront can read (OAC). Public download via CloudFront URL only.
resource "aws_s3_bucket_public_access_block" "apk" {
  bucket = aws_s3_bucket.apk.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront OAC: only CloudFront can read from S3
resource "aws_cloudfront_origin_access_control" "apk" {
  name                              = "${local.name_prefix}-apk-oac"
  description                       = "OAC for APK S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "apk" {
  enabled         = true
  is_ipv6_enabled = true
  comment         = "Emergency Medical Triage APK Download"
  price_class     = "PriceClass_100"

  origin {
    domain_name              = aws_s3_bucket.apk.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.apk.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.apk.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.apk.id}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    min_ttl     = 0
    default_ttl = 86400
    max_ttl     = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name        = "${local.name_prefix}-apk"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Allow only CloudFront to read from the bucket
data "aws_iam_policy_document" "apk_bucket_policy" {
  statement {
    sid    = "AllowCloudFrontServicePrincipal"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.apk.arn}/*"]
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.apk.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "apk" {
  bucket = aws_s3_bucket.apk.id
  policy = data.aws_iam_policy_document.apk_bucket_policy.json
}
