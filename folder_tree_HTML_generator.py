import os
import tkinter as tk
from tkinter import filedialog, messagebox
import webbrowser
import uuid
from datetime import datetime

class FolderTreeGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文件夹目录树结构HTML生成器")
        self.root.geometry("500x300")
        
        self.selected_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # 选择文件夹区域
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=10, padx=20, fill="x")
        
        tk.Label(folder_frame, text="选择文件夹:").pack(anchor="w")
        
        path_frame = tk.Frame(folder_frame)
        path_frame.pack(fill="x", pady=5)
        
        tk.Entry(path_frame, textvariable=self.selected_path, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="浏览", command=self.browse_folder).pack(side="right", padx=(5, 0))
        
        # 输出路径区域
        output_frame = tk.Frame(self.root)
        output_frame.pack(pady=5, padx=20, fill="x")
        
        tk.Label(output_frame, text="输出路径:").pack(anchor="w")
        
        path_frame2 = tk.Frame(output_frame)
        path_frame2.pack(fill="x", pady=5)
        
        tk.Entry(path_frame2, textvariable=self.output_path, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(path_frame2, text="浏览", command=self.browse_output).pack(side="right", padx=(5, 0))
        
        # 生成按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="生成目录树", command=self.generate_tree, bg="#4CAF50", fg="white", 
                 padx=20, pady=5).pack()
        
        # 状态标签
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=10)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 在Windows上将正斜杠转换为反斜杠显示
            if os.name == 'nt':
                folder_path = folder_path.replace('/', '\\')
            self.selected_path.set(folder_path)
            # 不再自动设置默认输出路径
    
    def browse_output(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            # 在Windows上将正斜杠转换为反斜杠显示
            if os.name == 'nt':
                folder_path = folder_path.replace('/', '\\')
            self.output_path.set(folder_path)
    
    def generate_tree(self):
        folder_path = self.selected_path.get()
        if not folder_path:
            messagebox.showerror("错误", "请选择一个文件夹")
            return
        
        # 将路径转换为标准格式用于处理
        normalized_path = folder_path.replace('\\', '/')
        if not os.path.exists(normalized_path):
            messagebox.showerror("错误", "选择的文件夹不存在")
            return
        
        try:
            self.status_label.config(text="正在生成目录树...")
            self.root.update()
            
            html_content = self.create_html_tree(normalized_path)
            output_file = self.save_html(html_content, normalized_path)
            
            # 在Windows上将路径显示为反斜杠格式
            display_output_file = output_file.replace('/', '\\') if os.name == 'nt' else output_file
            self.status_label.config(text=f"目录树已生成: {display_output_file}")
            messagebox.showinfo("成功", f"目录树已生成并保存到:\n{display_output_file}")
            
            # 询问是否打开文件
            if messagebox.askyesno("打开文件", "是否立即在浏览器中打开生成的HTML文件?"):
                webbrowser.open(f"file://{output_file}")
                
        except Exception as e:
            messagebox.showerror("错误", f"生成过程中出现错误:\n{str(e)}")
            self.status_label.config(text="生成失败")
    
    def create_html_tree(self, root_path):
        # 生成唯一的ID用于JavaScript操作
        tree_id = str(uuid.uuid4())
        
        # 生成HTML内容，使用Windows风格路径
        root_display_path = root_path.replace('/', '\\') if os.name == 'nt' else root_path
        
        # 生成HTML内容
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件夹目录树 - {os.path.basename(root_path)}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 100%;
        }}
        /* 修改：创建一个固定宽度的容器用于横向滚动 */
        .tree-container {{
            width: 100%;
            overflow-x: auto;
            margin: 20px 0;
            background-color: white;
            border: 1px solid #ddd;
            padding: 10px;
            box-sizing: border-box;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
            margin-top: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .note {{
            color: #666;
            font-style: italic;
            margin-bottom: 15px;
            padding: 5px;
            background-color: #f9f9f9;
            border-left: 3px solid #4CAF50;
        }}
        .search-box {{
            margin: 15px 0;
            padding: 10px;
            border: 1px solid #ddd;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
        }}
        .search-box input {{
            flex: 1;
            min-width: 200px;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }}
        .search-box button {{
            margin-left: 10px;
            padding: 8px 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        .search-box button:hover {{
            background: #4CAF50;
        }}
        .tree {{
            line-height: 1.8;
            white-space: nowrap;
            min-width: max-content; /* 确保内容不会被压缩 */
        }}
        .tree-item {{
            list-style-type: none;
            position: relative;
            margin: 0;
            padding: 0 0 0 25px;
        }}
        .tree-item:before {{
            content: '';
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            border-left: 1px dashed #ccc;
        }}
        .tree-item:after {{
            content: '';
            position: absolute;
            top: 15px;
            left: 0;
            width: 15px;
            height: 1px;
            border-top: 1px dashed #ccc;
        }}
        .tree-item:last-child:before {{
            height: 15px;
        }}
        .tree-item-root {{
            padding-left: 0;
        }}
        .tree-item-root:before {{
            display: none;
        }}
        .tree-item-root:after {{
            display: none;
        }}
        .folder-item {{
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
            position: relative;
            white-space: nowrap;
            width: fit-content;
            min-width: 100%;
        }}
        .folder-item.no-children {{
            cursor: default;
        }}
        .folder-item:hover {{
            background-color: #4CAF50; /* 浅绿色 */
        }}
        .folder-item.no-children:hover {{
            background-color: #4CAF50; /* 浅绿色 */
        }}
        .toggle-icon {{
            margin-right: 5px;
            width: 16px;
            text-align: center;
            flex-shrink: 0;
        }}
        .folder-icon {{
            margin-right: 8px;
            color: #FFA500;
            flex-shrink: 0;
        }}
        .folder-name {{
            color: #333;
            overflow: hidden;
            text-overflow: ellipsis;
            flex-grow: 1;
            text-align: left;
            cursor: pointer;
        }}
        /* 删除未使用的 .folder-info 样式和“添加复制提示样式”注释 */
        .children {{
            display: block;
            margin-top: 5px;
        }}
        .collapsed .children {{
            display: none;
        }}
        .collapsed > .folder-item .toggle-icon:before {{
            content: '▶';
        }}
        .folder-item .toggle-icon:before {{
            content: '▼';
        }}
        .folder-item .folder-icon:before {{
            content: '📁';
        }}
        .empty-folder .folder-item .folder-icon:before {{
            content: '📂';
        }}
        /* 隐藏没有子文件夹的项的切换图标 */
        .no-children .toggle-icon {{
            display: none;
        }}
        .highlight {{
            background-color: yellow;
            font-weight: bold;
        }}
        .no-results {{
            color: red;
            font-style: italic;
            padding: 10px;
        }}
        .control-buttons {{
            margin: 10px 0;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
        }}
        .control-buttons button {{
            margin-right: 10px;
            margin-bottom: 5px;
            padding: 8px 12px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        .control-buttons button:hover {{
            background: #4CAF50;
        }}
        #noResultsContainer {{
            color: red;
            font-style: italic;
            margin-left: 10px;
        }}
        @media (max-width: 768px) {{
            .search-box {{
                flex-direction: column;
                align-items: stretch;
            }}
            .search-box input {{
                margin-bottom: 10px;
            }}
            .search-box button {{
                margin-left: 0;
                width: 100%;
            }}
            .control-buttons {{
                flex-direction: column;
            }}
            .control-buttons button {{
                margin-right: 0;
                margin-bottom: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>文件夹目录树: {os.path.basename(root_path)}</h1>
        <div class="note">使用 Ctrl+鼠标左键 点击文件夹可以复制路径</div>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="输入文件夹名称进行搜索...">
            <button id="searchBtn">搜索</button>
        </div>
        
        <div class="control-buttons">
            <button id="expandAll">展开所有▼</button>
            <button id="collapseAll">收缩所有▶</button>
            <div id="noResultsContainer"></div>
        </div>
        
        <!-- 修改：添加一个容器用于横向滚动 -->
        <div class="tree-container">
            <div class="tree">
                <ul class="tree-item-root">
"""
        
        # 递归生成目录树
        html += self.generate_tree_items(root_path, root_path, is_root=True)
        
        html += """
                </ul>
            </div>
        </div>
    </div>

    <script>
        // 复制路径功能
        function copyPath(path, event) {
            event.stopPropagation();
            
            navigator.clipboard.writeText(path).then(function() {
                // 使用信息框提示替换气泡提示
                alert('复制路径成功');
            }).catch(function(err) {
                console.error('复制失败: ', err);
                alert('复制路径失败');
            });
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            // 只选择有子文件夹的目录项（即不包含no-children类的项）
            const folderItems = document.querySelectorAll('.folder-item:not(.no-children)');
            
            folderItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    // 防止事件冒泡
                    e.stopPropagation();
                    
                    const parentLi = this.closest('.tree-item');
                    parentLi.classList.toggle('collapsed');
                });
            });
            
            // 为所有文件夹名称添加Ctrl+点击事件
            const folderNames = document.querySelectorAll('.folder-name');
            folderNames.forEach(name => {
                name.addEventListener('click', function(e) {
                    // 如果按下了Ctrl键，则复制路径而不触发展开/收缩
                    if (e.ctrlKey) {
                        e.stopPropagation();
                        e.preventDefault();
                        // 从data-path属性获取路径
                        const path = this.getAttribute('data-path');
                        copyPath(path, e);
                    }
                });
            });
            
            // 默认折叠所有子目录
            const treeItems = document.querySelectorAll('.tree-item');
            treeItems.forEach(item => {
                if(!item.classList.contains('tree-item-root')) {
                    item.classList.add('collapsed');
                }
            });
            
            // 展开所有按钮功能
            document.getElementById('expandAll').addEventListener('click', function() {
                const treeItems = document.querySelectorAll('.tree-item');
                treeItems.forEach(item => {
                    item.classList.remove('collapsed');
                });
            });
            
            // 收缩所有按钮功能
            document.getElementById('collapseAll').addEventListener('click', function() {
                const treeItems = document.querySelectorAll('.tree-item');
                treeItems.forEach(item => {
                    if(!item.classList.contains('tree-item-root')) {
                        item.classList.add('collapsed');
                    }
                });
            });
            
            // 搜索功能
            const searchInput = document.getElementById('searchInput');
            let searchResults = []; // 存储搜索结果
            let currentResultIndex = 0; // 当前高亮的结果索引
            
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });
            
            searchInput.addEventListener('input', function(e) {
                if (e.target.value === '') {
                    clearSearch();
                }
            });
            
            document.getElementById('searchBtn').addEventListener('click', performSearch);
            
            function performSearch() {
                const searchTerm = searchInput.value.toLowerCase().trim();
                
                // 清除之前的高亮和结果
                clearSearch();
                
                if (searchTerm === '') {
                    return;
                }
                
                const folderNames = document.querySelectorAll('.folder-name');
                searchResults = [];
                currentResultIndex = 0;
                
                // 查找匹配的文件夹
                folderNames.forEach(name => {
                    const text = name.textContent;
                    if (text.toLowerCase().includes(searchTerm)) {
                        searchResults.push(name);
                    }
                });
                
                if (searchResults.length > 0) {
                    // 高亮第一个结果
                    highlightResult(0);
                    scrollToResult(0);
                } else {
                    // 显示未找到提示
                    showNoResultsMessage(searchTerm);
                }
            }
            
            function highlightResult(index) {
                // 清除之前的结果高亮
                searchResults.forEach((result, i) => {
                    if (i === index) {
                        result.classList.add('highlight');
                        // 展开包含匹配项的父级目录
                        let parent = result.closest('.tree-item');
                        while (parent && parent.classList.contains('tree-item')) {
                            parent.classList.remove('collapsed');
                            parent = parent.parentElement ? parent.parentElement.closest('.tree-item') : null;
                        }
                    } else {
                        result.classList.remove('highlight');
                    }
                });
            }
            
            function scrollToResult(index) {
                if (searchResults[index]) {
                    searchResults[index].scrollIntoView({behavior: 'smooth', block: 'center'});
                }
            }
            
            function clearSearch() {
                // 清除高亮
                const highlighted = document.querySelectorAll('.folder-name.highlight');
                highlighted.forEach(element => {
                    element.classList.remove('highlight');
                });
                
                // 移除"未找到"消息
                const noResultsContainer = document.getElementById('noResultsContainer');
                if (noResultsContainer) {
                    noResultsContainer.textContent = '';
                }
                
                searchResults = [];
                currentResultIndex = 0;
            }
            
            function showNoResultsMessage(term) {
                const noResultsContainer = document.getElementById('noResultsContainer');
                if (noResultsContainer) {
                    noResultsContainer.textContent = `未找到包含 "${term}" 的文件夹`;
                }
            }
        });
    </script>
</body>
</html>"""
        
        return html
    
    def generate_tree_items(self, path, root_path, is_root=False):
        html = ""
        
        # 获取所有子目录
        try:
            items = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
            items.sort(key=lambda x: x.lower())  # 按名称排序
        except PermissionError:
            items = []
        
        folder_name = os.path.basename(path) if not is_root else os.path.basename(path)
        # 计算相对路径
        relative_path = os.path.relpath(path, root_path) if not is_root else "."
        if relative_path == ".":
            display_path = os.path.basename(root_path)
        else:
            # 使用Windows风格的路径分隔符
            display_path = os.path.join(os.path.basename(root_path), relative_path).replace('/', '\\') if os.name == 'nt' else os.path.join(os.path.basename(root_path), relative_path)
        
        if not items:
            if not is_root:
                # 标记空文件夹
                html += '<li class="tree-item empty-folder">\n'
            else:
                html += '<li class="tree-item">\n'
            
            # 对于没有子文件夹的文件夹，添加 no-children 类
            html += f'    <div class="folder-item no-children">\n'
            html += f'        <span class="toggle-icon"></span>\n'
            html += f'        <span class="folder-icon"></span>\n'
            # 添加data-path属性用于存储路径
            # 修复：确保复制的路径使用Windows风格的单反斜杠
            data_path = display_path.replace('"', '&quot;')
            html += f'        <span class="folder-name" data-path="{data_path}">{folder_name}</span>\n'
            html += f'    </div>\n'
        else:
            html += '<li class="tree-item">\n'
            
            # 对于有子文件夹的文件夹，保留原有的切换功能
            html += f'    <div class="folder-item">\n'
            html += f'        <span class="toggle-icon"></span>\n'
            html += f'        <span class="folder-icon"></span>\n'
            # 添加data-path属性用于存储路径
            # 修复：确保复制的路径使用Windows风格的单反斜杠
            data_path = display_path.replace('"', '&quot;')
            html += f'        <span class="folder-name" data-path="{data_path}">{folder_name}</span>\n'
            html += f'    </div>\n'
            
            # 添加子目录
            html += '    <ul class="children">\n'
            for item in items:
                item_path = os.path.join(path, item)
                html += self.generate_tree_items(item_path, root_path)
            html += '    </ul>\n'
        
        html += '</li>\n'
        
        return html
    
    def save_html(self, html_content, root_path):
        # 生成输出文件路径，使用主目录名称+当前时间作为文件名
        output_dir = self.output_path.get() if self.output_path.get() else os.path.join(os.path.expanduser("~"), "Desktop")
        # 标准化输出目录路径
        output_dir = output_dir.replace('\\', '/')
        if not os.path.exists(output_dir):
            output_dir = os.getcwd()
        
        # 获取主目录名称
        root_name = os.path.basename(root_path)
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # 组合文件名
        filename = f"{root_name}_{current_time}.html"
        output_file = os.path.join(output_dir, filename)
        
        # 保存HTML文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return output_file
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FolderTreeGenerator()
    app.run()