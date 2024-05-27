current_epoch=$(date +%s)
target_epoch=$(date -d "$1" +%s)

sleep_seconds=$(( $target_epoch - $current_epoch ))

echo "Sleep for $sleep_seconds seconds until $1"
sleep $sleep_seconds
