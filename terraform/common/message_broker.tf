resource "aws_elasticache_cluster" "message_broker" {
  cluster_id           = "retro-message-broker"
  engine               = "redis"
  node_type            = "cache.t2.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis3.2"
  port                 = 6379

  security_group_ids = ["${aws_security_group.redis.id}"]
  subnet_group_name = "${aws_elasticache_subnet_group.private_subnets.name}"

  maintenance_window = "sun:00:00-sun:01:00"
}

resource "aws_elasticache_subnet_group" "private_subnets" {
  name = "private-subnets"
  description = "Private subnets"

  subnet_ids = ["subnet-99fc88b5", "subnet-4fc2f02b", "subnet-909ae79c", "subnet-e6216cbb", "subnet-5f713860", "subnet-99e8fed2"]
}

resource "aws_security_group" "redis" {
  name        = "redis"
  description = "Allow Redis DB communication"

  tags {
    Name = "redis"
  }
}

resource "aws_security_group_rule" "allow_redis_within_security_group" {
  type            = "ingress"
  from_port       = 6379
  to_port         = 6379
  protocol        = "tcp"
  source_security_group_id = "${aws_security_group.redis.id}"

  security_group_id = "${aws_security_group.redis.id}"
}

resource "aws_security_group_rule" "allow_all_to_anywhere" {
  type            = "egress"
  from_port       = 0
  to_port         = 0
  protocol        = "tcp"
  cidr_blocks     = ["0.0.0.0/0"]

  security_group_id = "${aws_security_group.redis.id}"
}
