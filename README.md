\# AWS VPC Infrastructure

A fully deployed AWS cloud infrastructure featuring a custom VPC, public/private subnets, NAT Gateway, EC2-hosted frontend and backend applications, and an Application Load Balancer.



\## Live Demo

\*\*Application URL:\*\* http://aisha-alb-1627282953.us-east-1.elb.amazonaws.com  

\*\*Stack:\*\* Python Flask (frontend + backend) · AWS ALB · Custom VPC



\## Architecture Diagram

Internet

│

▼

┌─────────────────────────────────────────────────────┐

│ aisha-test-vpc (10.0.0.0/16) │

│ │

│ ┌─────────────────────┐ ┌────────────────────┐ │

│ │ aisha-public-sn │ │ aisha-public-sn │ │

│ │ -us-east1a │ │ -us-east1b │ │

│ │ 10.0.1.0/24 │ │ 10.0.3.0/24 │ │

│ │ │ │ │ │

│ │ ┌───────────────┐ │ │ ┌─────────────┐ │ │

│ │ │ NAT Gateway │ │ │ │ ALB │ │ │

│ │ │ nat-1681e9a.. │ │ │ │ port :80 │ │ │

│ │ │ (Elastic IP) │ │ │ └──────┬──────┘ │ │

│ │ └───────────────┘ │ │ │ │ │

│ └─────────────────────┘ └─────────┼──────────┘ │

│ │ │

│ ┌─────────────────────┐ ┌─────────▼──────────┐ │

│ │ aisha-private-sn │ │ aisha-private-sn │ │

│ │ -us-east1a │ │ -us-east1b │ │

│ │ 10.0.2.0/24 │ │ 10.0.4.0/24 │ │

│ │ │ │ │ │

│ │ ┌───────────────┐ │ │ ┌───────────────┐ │ │

│ │ │ Frontend EC2 │◄─┼──┼──│ Backend EC2 │ │ │

│ │ │ Flask :80 │ │ │ │ Flask :5000 │ │ │

│ │ │ No Public IP │ │ │ │ No Public IP │ │ │

│ │ └───────────────┘ │ │ └───────────────┘ │ │

│ └─────────────────────┘ └─────────────────────┘ │

└─────────────────────────────────────────────────────┘





\*\*Traffic flow:\*\*  

User → ALB (public subnet) → Frontend EC2 (private subnet) → \[Flask proxy] → Backend EC2 (private subnet)



\## Infrastructure Components



| Resource | Name | Details |

|----------|------|---------|

| VPC | aisha-test-vpc | 10.0.0.0/16 |

| Public Subnet 1 | aisha-public-sn-us-east1a | 10.0.1.0/24 · us-east-1a |

| Public Subnet 2 | aisha-public-sn-us-east1b | 10.0.3.0/24 · us-east-1b |

| Private Subnet 1 | aisha-private-sn-us-east1a | 10.0.2.0/24 · us-east-1a |

| Private Subnet 2 | aisha-private-sn-us-east1b | 10.0.4.0/24 · us-east-1b |

| Internet Gateway | - | Attached to VPC |

| NAT Gateway | nat-1681e9a923e3d876a | Single AZ · Elastic IP · public subnet 1 |

| Route Table (public) | - | 0.0.0.0/0 → IGW |

| Route Table (private) | - | 0.0.0.0/0 → NAT GW |

| Backend EC2 | - | t2.micro · private-subnet-2 · No public IP · 10.0.4.233 |

| Frontend EC2 | - | t2.micro · private-subnet-1 · No public IP |

| Load Balancer | aisha-alb-1627282953 | Internet-facing · public subnets |

| Target Group | - | HTTP:80 · health check on / |



\## Security Design



| Resource | Inbound Rule | Source |

|----------|--------------|--------|

| alb-sg | HTTP port 80 | 0.0.0.0/0 (internet) |

| frontend-sg | HTTP port 80 | alb-sg only |

| backend-sg | TCP port 5000 | frontend-sg only |



\- ✅ EC2 instances have \*\*no public IP addresses\*\*

\- ✅ Backend is \*\*not reachable\*\* from the internet under any path

\- ✅ Frontend only accepts traffic originating from the ALB

\- ✅ No SSH inbound rules — shell access via AWS SSM Session Manager only

\- ✅ Private subnets reach the internet \*\*outbound-only\*\* through the NAT Gateway



\## Application



\### Backend — Python Flask API

Runs on port 5000 on the backend EC2 in private-subnet-2 (10.0.4.0/24).



\*\*Endpoints:\*\*

\- `GET /api/message` → `{ "message": "Hello from backend" }`



\### Frontend — Python Flask + HTML/JS

Runs on port 80 on the frontend EC2 in private-subnet-1 (10.0.2.0/24). Flask serves the HTML page and proxies `/api/\*` requests to the backend's private IP on port 5000. The browser never communicates directly with the backend.



\## Deployment Steps



\### Prerequisites

\- AWS account with AdministratorAccess

\- Region: us-east-1 (all resources must be in the same region)

\- EC2 key pair created in the region



\### 1. VPC \& Networking

1\. \*\*VPC Console → Create VPC (VPC only)\*\*

&#x20;  - CIDR: 10.0.0.0/16

&#x20;  - Name: aisha-test-vpc



2\. \*\*Create 4 subnets:\*\*

&#x20;  - aisha-public-sn-us-east1a  10.0.1.0/24  us-east-1a

&#x20;  - aisha-public-sn-us-east1b  10.0.3.0/24  us-east-1b

&#x20;  - aisha-private-sn-us-east1a 10.0.2.0/24  us-east-1a

&#x20;  - aisha-private-sn-us-east1b 10.0.4.0/24  us-east-1b



3\. \*\*Create Internet Gateway\*\* → Attach to VPC



4\. \*\*Create NAT Gateway:\*\*

&#x20;  - Subnet: aisha-public-sn-us-east1a

&#x20;  - Allocate new Elastic IP

&#x20;  - NAT Gateway ID: nat-1681e9a923e3d876a



5\. \*\*Create Route Tables:\*\*

&#x20;  - Public Route Table → route 0.0.0.0/0 to IGW → associate public subnets

&#x20;  - Private Route Table → route 0.0.0.0/0 to NAT → associate private subnets



\### 2. Security Groups

1\. \*\*alb-sg\*\* → inbound HTTP:80 from 0.0.0.0/0

2\. \*\*frontend-sg\*\* → inbound HTTP:80 from alb-sg

3\. \*\*backend-sg\*\* → inbound TCP:5000 from frontend-sg



\### 3. EC2 Instances

\*\*Launch backend-ec2:\*\*

\- AMI: Ubuntu 22.04 (or Amazon Linux 2023)

\- Subnet: aisha-private-sn-us-east1b (10.0.4.0/24)

\- No public IP

\- Security group: backend-sg

\- User data: Install Python3, Flask, and run app.py



\*\*Launch frontend-ec2:\*\*

\- AMI: Ubuntu 22.04 (or Amazon Linux 2023)

\- Subnet: aisha-private-sn-us-east1a (10.0.2.0/24)

\- No public IP

\- Security group: frontend-sg

\- User data: Install Python3, Flask, requests, and run app.py



\### 4. Connect Frontend → Backend

After both instances are running, get the private IP of backend-ec2 (10.0.4.233) from the EC2 console.



Update frontend app.py with the correct BACKEND\_URL:

```python

BACKEND\_URL = "http://10.0.4.233:5000"



5\. Load Balancer

Create Target Group:



Name: aisha-frontend-tg



Type: Instances | Protocol: HTTP | Port: 80



Health check path: /



Register: frontend-ec2



Create Application Load Balancer:



Name: aisha-alb-1627282953



Scheme: Internet-facing



Subnets: aisha-public-sn-us-east1a, aisha-public-sn-us-east1b



Security group: alb-sg



Listener: HTTP:80 → forward to aisha-frontend-tg



6\. Test

Open http://aisha-alb-1627282953.us-east-1.elb.amazonaws.com in a browser and click "Get Message from Backend".

Expected response: Hello from backend



Screenshots

See the /screenshots folder for:



01-Vpc.png — VPC configuration



02-VpcSubnets.png — All 4 subnets with CIDRs



03-RouteTables.png — Public and private route tables with routes



04-NatGateway.png — NAT Gateway in public subnet with Elastic IP



05-EC2.png — Both EC2 instances showing private IPs



06-LoadBalancer.png — ALB active, public subnets, listener on port 80



07-TargetGroup.png — Target group with frontend-ec2 showing healthy



08-SecurityGroups.png — All three security groups with rules



09-WorkingApp.png — Browser showing the live application via ALB DNS



Networking Explanation

The VPC (10.0.0.0/16) is an isolated virtual network. It is divided into four subnets across two Availability Zones.



Public subnets (10.0.1.0/24 and 10.0.3.0/24) have a route to the Internet Gateway, so resources in them can communicate with the internet bidirectionally (given a public IP or Elastic IP). The ALB lives here — it is the only entry point from the internet.



Private subnets (10.0.2.0/24 and 10.0.4.0/24) have no route to the Internet Gateway, so nothing on the internet can initiate a connection to resources inside them. The EC2 instances live here. To make outbound internet requests (package installs, AWS API calls), traffic from private subnets routes through the NAT Gateway. The NAT Gateway translates their private IPs to its Elastic IP for outbound traffic, but allows no unsolicited inbound connections.



Security Groups add a second layer: even within the VPC, the backend only accepts connections from the frontend security group, and the frontend only accepts connections from the ALB security group. This enforces least-privilege at the network level.



Acceptance Criteria

✅ VPC created with 2 public and 2 private subnets



✅ NAT Gateway configured in single AZ (public subnet 1)



✅ Route tables configured correctly (public → IGW, private → NAT)



✅ Backend EC2 deployed in private subnet with no public IP



✅ Frontend EC2 deployed in private subnet with no public IP



✅ Load Balancer deployed in public subnets



✅ Frontend accessible via Load Balancer DNS



✅ Frontend successfully communicates with backend



✅ Required documentation submitted



Repository Structure



aws-infrastructure-project/

├── backend/

│   ├── app.py              # Flask API

│   └── requirements.txt    # Python dependencies

├── frontend/

│   ├── app.py              # Flask app with proxy

│   └── requirements.txt    # Python dependencies

├── screenshots/            # AWS Console screenshots

└── README.md



