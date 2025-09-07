from lxml import etree
'''
svg语法
<path fill="rgb(254,250,241)" 
stroke="rgb(254,250,241)" 
stroke-width="1" 
opacity="1" 
d="M 648.5 91 L 665.5 91 L 696.5 97 L 720.5 107 L 723.5 107 L 735 113.5 L 735.5 115 L 737 114.5 L 736.5 116 L 738.5 115 Q 741.5 116.5 738.5 118 Q 728.6 109.9 714.5 106 L 714.5 107 Q 748.7 122.3 772 148.5 L 782 161.5 L 785 170 Q 787.7 168.9 787 171.5 L 789 174.5 L 790 192.5 L 784 213.5 L 786 212.5 L 791.5 197 L 792 200.5 Q 788.7 214.2 780 222.5 L 784 225.5 L 782.5 225 Q 779.8 222.2 773.5 223 L 772 221.5 L 773.5 222 L 777 220.5 L 780 211.5 L 780 207.5 L 778 196.5 L 774 185.5 Q 760 164 742 146.5 L 741 143.5 L 751 152.5 Q 765.8 167.2 777 185.5 L 781 195.5 L 781 202.5 L 782.5 208 L 784 197 L 782 196.5 L 784 196 L 785 192.5 L 783.5 187 L 782.5 191 L 781 179.5 L 769 157.5 L 759 143 L 752 139 L 750.5 136 L 736.5 126 L 709 112.5 Q 707.2 106.4 714.5 109 L 717.5 110 L 717.5 109 L 693.5 99 L 677.5 96 L 677.5 97 L 680 98.5 L 675.5 100 L 668 98 Q 669.3 95 665.5 96 L 665.5 94 L 663.5 95 L 660.5 94 L 649.5 93 L 648.5 94 L 631.5 95 L 619.5 98 L 619.5 97 L 631.5 93 L 647.5 92 L 648.5 91 Z " />
'''

class SvgImage():
    def __init__(self,filepath:str):
        '''
        初始化Svg图片对象

        创建Svg对象时，需要提供svg文件的地址

        Args:
        filepath:svg文件的地址（字符串，非空）

        Raises:

        '''
        try :
            self.tree=etree.parse(filepath)#解析svg文件
            ns = {"svg" : "http://www.w3.org/2000/svg"}#指定命名空间
            self.paths=self.tree.xpath("//svg:path",namespaces=ns)#获取所有path标签
            self.svg=self.tree.xpath("//svg:svg",namespaces=ns)#获取svg标签
        except:
            raise RuntimeError("初始化Svg图片对象失败")
    def getpaths(self) -> list:
        '''
        获取所有path组成的列表

        获取所有path组成的列表，其中每个path都是一个字典

        Returns:
        返回由该文件中所有path标签组成的一个列表

        Example:
        >>> p=SvgImage(filename)
        >>> p.getpaths()
        [{'d': 'M0 0 C211.2 0 422.4 0 640 0 C640 211.2 640 422.4 640 640 C428.8 640 217.6 640 0 640 C0 428.8 0 217.6 0 0 Z ', 'fill': '#FECB02', 'transform': 'translate(0,0)'},...]
        '''
        paths=[]
        for element in self.paths:
            paths.append(element.attrib)
        return paths
    def getviewbox(self) -> tuple:
        '''
        获取viewbox的大小
        
        获取svg文件对应到bas弹幕中的viewbox的大小

        returns:
        返回一个二元元组，第一项为viewbox的长，第二项为viewbox的宽

        Example：
        >>> p=SvgImage(filename)
        >>> p.getviewbox()
        (640,1280)
        '''
        width=self.svg[0].attrib["width"]
        height=self.svg[0].attrib["height"]
        return (width,height)
    def _output(self):
        '''
        仅供测试使用，随时更改
        '''
        for element in self.paths:
            print(element.attrib)
class DefPath():
    def __init__(self,viewbox:tuple,path:dict,id:str,zindex:int=1):
        '''
        初始化DefPath对象

        按照bas的语法给path标签的每个属性分别赋值

        Args:
        viewbox:viewbox的大小，是SvgImage.getviewbox()的返回值，是一个元组，第一项是长，第二项是宽
        path:是一个字典，是SvgImage.getpaths()的返回值的任意一项
        id:是一个字符串，是bas定义path时给这个path的名称
        zindex:是一个整数，层次权重，值高的对象在上层
        '''
        self.viewBox=f'\"0 0 {viewbox[0]} {viewbox[1]}\"'
        self.d="\""+path["d"]+"\""
        self.fillColor = "0x"+path["fill"][1:]
        self.zIndex=zindex
        temp=path["transform"].replace("translate(","").replace(")","").split(",")#把translate(x,y)转换成[x,y]
        self.x=temp[0]
        self.y=temp[1]
        self.id=id
    def tobaspath(self) -> str:
        '''
        生成bas格式的path
        生成一个bas格式的path，返回一个字符串
        
        example:
        >>>p1=DefPath(img.getviewbox(),paths[0],"p1",1)
        >>>p1.tobaspath()
        def path p1 {
            d="M0 0 C211.2 0 422.4 0 640 0 C640 211.2 640 422.4 640 640 C428.8 640 217.6 640 0 640 C0 428.8 0 217.6 0 0 Z "
            viewBox="0 0 640 640"
            x=0
            y=0
            fillColor=0xFECB02
            zIndex=1
        }
        '''
        baspath=\
        f"""
        def path {self.id} {{
            d={self.d}
            viewBox={self.viewBox}
            x={self.x}
            y={self.y}
            fillColor={self.fillColor}
            zIndex={self.zIndex}
        }}

        """
        return baspath
def tobas(viewbox:tuple,paths:list,time:int=1000,outputfile:str="outputbas.txt")->str:
    try:
        with open(outputfile,"w") as f:
            for i in range(len(paths)):
                content=DefPath(viewbox,paths[i],f"p{i}").tobaspath()
                f.write(content)
            for i in range(len(paths)):
                f.write(f"set p{i} {{}} {time}ms\n")
        return "success"
    except:
        return "failed"
if __name__=="__main__":
    img=SvgImage("test.svg")
    paths=img.getpaths()
    viewbox=img.getviewbox()
    tobas(viewbox,paths)
    input()
