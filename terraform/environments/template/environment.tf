resource "aws_elastic_beanstalk_environment" "env" {
  name = "${var.application}-${var.environment}"
  description = "The retrospective ${var.environment} environment"
  application = "${var.application}"

  cname_prefix = "${var.application}-${var.environment}"

  wait_for_ready_timeout = "30m"

  # Software

  setting {
    namespace = "aws:elasticbeanstalk:container:python"
    name = "WSGIPath"
    value = "retrospective/wsgi.py"
  }

  setting {
    namespace = "aws:elasticbeanstalk:container:python"
    name = "NumProcesses"
    value = "1"
  }

  setting {
    namespace = "aws:elasticbeanstalk:container:python"
    name = "NumThreads"
    value = "15"
  }

  setting {
    namespace = "aws:elasticbeanstalk:xray"
    name = "XRayEnabled"
    value = "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:hostmanager"
    name = "LogPublicationControl"
    value = "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:cloudwatch:logs"
    name = "StreamLogs"
    value = "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:container:python:staticfiles"
    name = "/view/"
    value = "frontend/view/"
  }

  setting {
    namespace = "aws:elasticbeanstalk:container:python:staticfiles"
    name = "/create/"
    value = "frontend/create/"
  }

  setting {
    namespace = "aws:elasticbeanstalk:container:python:staticfiles"
    name = "/join/"
    value = "frontend/join/"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name = "ENVIRONMENT"
    value = "${var.environment}"
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name = "SECRET_KEY"
    value = "${var.secret_key}"
  }

  # Instances

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name = "InstanceType"
    value = "t2.micro"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name = "MonitoringInterval"
    value = "5 minute"
  }

  # Capacity

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name = "EnvironmentType"
    value = "SingleInstance"
  }

  # Roling updates and deployments

  setting {
    namespace = "aws:elasticbeanstalk:command"
    name = "DeploymentPolicy"
    value = "Immutable"
  }

  setting {
    namespace = "aws:autoscaling:updatepolicy:rollingupdate"
    name = "RollingUpdateType"
    value = "Immutable"
  }

  setting {
    namespace = "aws:elasticbeanstalk:command"
    name = "IgnoreHealthCheck"
    value = "false"
  }

  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name = "HealthCheckSuccessThreshold"
    value = "Ok"
  }

  setting {
    namespace = "aws:elasticbeanstalk:command"
    name = "Timeout"
    value = "600"
  }

  # Security

  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name = "ServiceRole"
    value = "${var.service_role}"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name = "EC2KeyName"
    value = "${var.ec2_key_name}"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name = "IamInstanceProfile"
    value = "${module.permissions.instance_profile}"
  }

  # Monitoring

  setting {
    namespace = "aws:elasticbeanstalk:application"
    name = "Application Healthcheck URL"
    value = "/api/health"
  }

  setting {
    namespace = "aws:elasticbeanstalk:healthreporting:system"
    name = "SystemType"
    value = "enhanced"
  }

  # Managed updates

  setting {
    namespace = "aws:elasticbeanstalk:managedactions"
    name = "ManagedActionsEnabled"
    value = "true"
  }

  setting {
    namespace = "aws:elasticbeanstalk:managedactions"
    name = "PreferredStartTime"
    value = "SUN:09:00"
  }

  setting {
    namespace = "aws:elasticbeanstalk:managedactions:platformupdate"
    name = "UpdateLevel"
    value = "minor"
  }

  setting {
    namespace = "aws:elasticbeanstalk:managedactions:platformupdate"
    name = "InstanceRefreshEnabled"
    value = "false"
  }

  # Notifications

  setting {
    namespace = "aws:elasticbeanstalk:sns:topics"
    name = "Notification Endpoint"
    value = "${var.notification_email}"
  }

  setting {
    namespace = "aws:elasticbeanstalk:sns:topics"
    name = "Notification Topic Name"
    value = "${var.application}-${var.environment}"
  }

  # Network

  setting {
    namespace = "aws:ec2:vpc"
    name = "VPCId"
    value = "vpc-c52067bc"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name = "AssociatePublicIpAddress"
    value = "true"
  }

  setting {
    namespace = "aws:ec2:vpc"
    name = "Subnets"
    value = "subnet-125b725a,subnet-6efa090a,subnet-e8d3bfb2,subnet-f6d39dd9"
  }

  # Database - nothings

  tags {
    environment = "${var.environment}"
  }
}
