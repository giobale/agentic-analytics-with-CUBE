FROM mysql:8.0

# Install required packages for CSV processing
RUN microdnf update && \
    microdnf install -y python3 python3-pip && \
    pip3 install mysql-connector-python pandas && \
    microdnf clean all

# Set secure file privileges for CSV loading
ENV MYSQL_ALLOW_EMPTY_PASSWORD=no

# Create directory for CSV files
RUN mkdir -p /var/lib/mysql-files/csv-data && \
    chown -R mysql:mysql /var/lib/mysql-files

# Copy scripts
COPY scripts/ /mysql-container/scripts/
RUN chmod +x /mysql-container/scripts/*.sh /mysql-container/scripts/*.py

# Copy custom entrypoint
COPY scripts/custom-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

# Use custom entrypoint that starts both MySQL and CSV service
ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]
CMD ["mysqld"]