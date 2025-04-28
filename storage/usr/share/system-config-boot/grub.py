import string

def readBootDB():
    bootlist=[]
    num = 0

    try:
        fd = open('/boot/grub/grub.conf', 'r')
    except:
        return None

    lines = fd.readlines()
    fd.close()
    for line in lines:
        if line[0] != "#":
            line = string.strip(line)

            try:
                line = string.split(line, '#')[0]
            except: 
                pass

            tokens = string.split(line)

            if tokens == None or tokens == "" or tokens == [] \
                    or tokens == ['']:
                continue
             
            if tokens[0] == "title":
                title = string.join(tokens[1:])
                bootlist.append(title)
                num += 1                
             
            if tokens[0].find("=") >= 0:
                tokens = string.split(tokens[0], "=")

            if tokens != [''] and tokens[0] == "default":
                try:
                    probedBoot = int(tokens[1])
                except:
                    probedBoot = 0
                continue

            if tokens != [''] and tokens[0] == "timeout":
                try:
                    probedTimeout = int(tokens[1])
                except:
                    probedTimeout = 0
                continue

    return probedBoot, probedTimeout, bootlist

def writeBootFile(timeout, num):
    # Read grub.conf
    try:
        fd = open('/etc/grub.conf', 'r')
    except:
        return None
    
    lines = fd.readlines()
    fd.close()
    defaultset = None
    timeoutset = None

    for i in xrange(len(lines)):
        if lines[i][0] != "#":
            line = string.strip(lines[i])
            try:
                line = string.split(line, '#')[0]
            except: 
                pass
            tokens = string.split(line)

            if not tokens or tokens == [] or tokens == ['']:
                continue

            if tokens[0].find("=") >= 0:
                tokens = string.split(tokens[0], "=")

            if tokens[0] == "timeout":
                lines[i] = "timeout=%d\n" % timeout
                timeoutset = 1
                continue

            if tokens[0] == "default":
                lines[i] = "default=%d\n" % num
                defaultset = 1
                continue

    if not defaultset:
        lines.append("default=%d\n" % num)

    if not timeoutset:
        lines.append("timeout=%d\n" % timeout)

    try:
        fd = open('/etc/grub.conf', 'w')
        fd.writelines(lines)
        fd.close()
    except:
        return None
