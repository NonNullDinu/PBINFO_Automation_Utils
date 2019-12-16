read -p 'Username: ' user -r
read -p 'Password: ' -s password -r
printf "[pbinfo]\nuser=%s\nparola=%s\n" "$user" "$password" > user_data.ini
echo
