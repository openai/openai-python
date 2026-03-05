# generate a text file with random data for testing file uploads
wanted_size=$((1024*2048*512))
file_size=$(( ((wanted_size/12)+1)*12 ))
read_size=$((file_size*3/4))

echo "wanted=$wanted_size file=$file_size read=$read_size"

dd if=/dev/urandom bs=$read_size count=1 | base64 > /tmp/small_test_file.txt

truncate -s "$wanted_size" /tmp/big_test_file.txt 
