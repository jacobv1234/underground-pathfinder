# JSON format guide

# |< marks the start of a branch that connects
# to the stations before it - prefix
# |> marks a branch connecting after - prefix
# || marks the last station of a branch - prefix
# ||> and ||< combine the above - prefix

# The station that connects to the mainline is the station
# closest to the connecting station <first >last

# >> means that the station can only be reached from
# the previous (one way path) - suffix
# << is the reverse - suffix

# load lines
import json
file = open("lines.json","r")
lines = json.load(file)
file.close()

# start and destination input
start = input("Enter a starting station: ")
end = input("Enter the destination: ")

# find line and location on line of start
startlines = []
startindexes = []
linenames = list(lines.keys())
for linename in linenames:
    line = lines[linename]
    for i in range(len(line)):
        check = str(line[i]).strip('|').strip('<').strip('>').lower()
        if start.lower() == check:
            startlines.append(linename)
            startindexes.append(i)
    
print(startlines)

# same for end
endlines = []
endindexes = []
for linename in linenames:
    line = lines[linename]
    for i in range(len(line)):
        check = str(line[i]).strip('|').strip('<').strip('>').lower()
        if end.lower() == check:
            endlines.append(linename)
            endindexes.append(i)

print(endlines)

# check for any matching lines
linematches = []
start_i = []
end_i = []
for i in range(len(startlines)):
    line = startlines[i]
    for j in range(len(endlines)):
        check = endlines[j]
        if line == check:
            linematches.append(line)
            start_i.append(startindexes[i])
            end_i.append(endindexes[j])

print(linematches)

# find what stations can be reached in a single train
one_train = {}
for i in range(len(startlines)):
    stationnumber = startindexes[i]
    line = lines[startlines[i]]
    reachableonline = []

    # check forwards - if || is found before |< or |> it is in a branch
    onbranch = False
    for j in range(stationnumber,len(line)):
        if '||' in line[j]:
            onbranch = True
            break
        if '|<' in line[j] or '|>' in line[j]:
            break

    # try forwards through the list
    skip = False
    while stationnumber < len(line):
        station = line[stationnumber]
        stationnumber += 1

        if '|>' in station:
            skip = True
        
        #if '||' in station:
            
            

        if station[-2:] == '<<' or skip:
            if '||' in station and skip:
                skip = False
            continue
            
        station = station.strip('|').strip('<').strip('>').lower()
        reachableonline.append(station)
