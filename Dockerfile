# Import armv8 parser runtime
FROM multiarch/qemu-user-static:x86_64-aarch64 as qemu

# Compile Stage
FROM arm64v8/python:3-slim AS compile-image

# Copy qemu
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin

RUN apt-get update
RUN apt-get install -y build-essential gcc libffi6 libffi-dev libssl-dev procps

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

# Running Stage
FROM arm64v8/python:3-slim AS runtime-image

# Copy qemu
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin

# Copy requirements
COPY --from=compile-image /root/.local /root/.local

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Copy application sources
WORKDIR /app
COPY . .

# Run the application
CMD [ "python", "./main.py" ]