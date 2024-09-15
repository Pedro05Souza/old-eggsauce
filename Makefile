# Variables for different OS setups
UNIX_SETUP_SCRIPT = ./setup.sh
WINDOWS_SETUP_SCRIPT = cmd/Csetup.bat

# Default target
all: build

# Setup for Unix-based OS
setup-unix: requirements.txt
	@echo "Running Unix setup..."
	$(UNIX_SETUP_SCRIPT)

# Setup for Windows OS
setup-windows: requirements.txt
	@echo "Running Windows setup..."
	$(WINDOWS_SETUP_SCRIPT)

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose up --build

# Check Docker containers (stop and remove them)
check:
	@echo "Stopping and removing Docker containers..."
	docker-compose down

# Run Docker containers
run:
	@echo "Starting Docker containers..."
	docker-compose up

# Clean up Docker images and containers
clean:
	@echo "Cleaning up Docker images and containers..."
	docker-compose down --rmi all --volumes --remove-orphans
