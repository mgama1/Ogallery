import qtawesome as qta

from custom import *

pixmap1 = QPixmap(qta.icon('mdi.jellyfish',color='#faf7f7').pixmap(400,400))
pixmap2 = QPixmap(qta.icon('mdi.fullscreen-exit',color='#e2172b').pixmap(200,200))
combined_pixmap = CustomAwesome().concat_pixmaps(pixmap1, pixmap2,2)
combined_pixmap.save('angry.png')


pixmap1 = QPixmap(qta.icon('mdi.jellyfish',color='#faf7f7').pixmap(400,400))
pixmap2 = QPixmap(qta.icon('mdi.glasses',color='#000000').pixmap(200,200))

combined_pixmap=CustomAwesome().concat_pixmaps(pixmap1, pixmap2,3)
combined_pixmap.save('info.png')


pixmap1 = QPixmap(qta.icon('mdi.jellyfish',color='#faf7f7').pixmap(400,400))
pixmap2 = QPixmap(qta.icon('fa.exclamation',color='#fde01a').pixmap(200,200))
combined_pixmap = CustomAwesome().concat_pixmaps(pixmap1, pixmap2,1.5)
combined_pixmap.save('warning.png')