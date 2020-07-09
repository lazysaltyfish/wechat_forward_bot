FROM multiarch/qemu-user-static:x86_64-aarch64 as qemu

FROM arm64v8/python:3-slim

# Copy qemu
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin

# Install requirements
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --prefer-binary --no-cache-dir -r requirements.txt

# Copy application sources
COPY . .

# Run the application
CMD [ "python", "./main.py" ]