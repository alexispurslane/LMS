import tdl

tdl.setFont('font/consolas/12x12_gs_tc.png', grayscale=True, altLayout=True)
console = tdl.init(80, 80, 'Test')
while True:
    console.clear()
    for i in range(100):
        console.drawChar(math.floor(i/80), i, )
    tdl.flush()
