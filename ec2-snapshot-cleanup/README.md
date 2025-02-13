## ec2 snapshot cleanup

1. **find_ami.py** looks through specified AWS accounts for AMI's with a specific keyword and generates a .csv file

2. You can then run **find_snapshots.py** which takes the output and looks for snapshots associated with the AMI ID's

note: you will need to modify variables **profiles** & **keyword** in **find_ami.py**