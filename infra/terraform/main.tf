# VPC Resources
# -----------------------------------------------------------------------------

resource "aws_vpc" "devops_vpc" {
  cidr_block = "10.0.0.0/16"
  tags       = { Name = "DevOps-vpc" }
}

# Subnets
resource "aws_subnet" "subnet_a" {
  vpc_id                  = aws_vpc.devops_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "eu-west-2a"
  tags                    = { Name = "subnet-a" }
}

resource "aws_subnet" "subnet_b" {
  vpc_id                  = aws_vpc.devops_vpc.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "eu-west-2b"
  tags                    = { Name = "subnet-b" }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.devops_vpc.id
  tags   = { Name = "DevOps-igw" }
}

# Public Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.devops_vpc.id

  route {
    # Default route for all internet traffic
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = { Name = "public-rt" }
}

# Route Table Associations (making subnets public)
resource "aws_route_table_association" "subnet_a_assoc" {
  subnet_id      = aws_subnet.subnet_a.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "subnet_b_assoc" {
  subnet_id      = aws_subnet.subnet_b.id
  route_table_id = aws_route_table.public_rt.id
}


# Security Group
# -----------------------------------------------------------------------------

resource "aws_security_group" "devops_sg" {
  name        = "devops-sg"
  description = "Allow SSH, HTTP, NodePort"
  vpc_id      = aws_vpc.devops_vpc.id

  # Ingress: SSH from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Ingress: HTTP from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Ingress: Jenkins from anywhere
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Ingress: Kubernetes NodePort range from anywhere
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress: Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # Represents all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "devops-sg" }
}


# Key Pair
# -----------------------------------------------------------------------------

resource "aws_key_pair" "oeson_key" {
  key_name   = "oesonproject.pem"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCvU9Z74MWQ5U5pOkj2IhUfYAoV4W4bq928Cl3+Os18RhQ+PGHNa6KOhzkKTLLSXSX8inusAuVnA8wivvarhf88tQrtDvmJHKoWv1cTf9tVJxFinQ7F8CXWD9ZNJ2IbE/vmejA+4I/5ZNuVJWMB7TmwUQ5xv2HZp3+Mw+9kP4iks4Vf4YMI1pSpoVAvi4dt++pBbm6KmiktxPx1e3fwH4L5/z/qH/t3GwfpYQiMye8PN85SLfu1DgsmhIu40l5Xj9REu3FmzHr6awjSLDrrtlHe0bQmJQ4so03FfBGgqa5GIWLyZGnQBhookRhzJ8050ur2pUQlEPWY9NFOnBahsYez"
  #file("/c/Users/vanmo/Downloads/oesonproject.pub")
  tags = {
    Name = "oeson-key"

  }
}


# EC2 Instances
# -----------------------------------------------------------------------------

# AMI ID is for Ubuntu 22.04 LTS in eu-west-2 (London)
locals {
  ami_id = "ami-046c2381f11878233"
}

resource "aws_instance" "jenkins_host" {
  ami                    = local.ami_id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.subnet_a.id
  vpc_security_group_ids = [aws_security_group.devops_sg.id]
  key_name               = aws_key_pair.oeson_key.key_name
  tags                   = { Name = "Jenkins-host" }
}

resource "aws_instance" "k8s_node_1" {
  ami                    = local.ami_id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.subnet_b.id
  vpc_security_group_ids = [aws_security_group.devops_sg.id]
  key_name               = aws_key_pair.oeson_key.key_name
  tags                   = { Name = "k8s-node-1" }
}

resource "aws_instance" "k8s_node_2" {
  ami                    = local.ami_id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.subnet_b.id
  vpc_security_group_ids = [aws_security_group.devops_sg.id]
  key_name               = aws_key_pair.oeson_key.key_name
  tags                   = { Name = "k8s-node-2" }
}


