SOURCE=$1
TARGET=$2

while inotifywait -r $SOURCE/*; do
    rsync -avz $SOURCE $TARGET
done
