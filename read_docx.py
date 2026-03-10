import zipfile
import xml.etree.ElementTree as ET
import sys

def read_docx(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as docx:
            content = docx.read('word/document.xml')
            tree = ET.fromstring(content)
            
            # The XML namespaces usually used in docx
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            text = []
            for paragraph in tree.findall('.//w:p', namespaces):
                para_text = []
                for run in paragraph.findall('.//w:r', namespaces):
                    text_node = run.find('w:t', namespaces)
                    if text_node is not None and text_node.text:
                        para_text.append(text_node.text)
                if para_text:
                    text.append(''.join(para_text))
            return '\n'.join(text)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(read_docx(sys.argv[1]))
    else:
        print("Please provide a file path")
