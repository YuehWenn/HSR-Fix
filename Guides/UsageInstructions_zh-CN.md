[EN](UsageInstructions.md) | 中文

## 使用指南

**下面是关于如何使用 GIMI 和 HSR-Fix 对星穹铁道进行模型与贴图修改的介绍。**

### 修改模型

在阅读前你需要了解 GIMI 与 blender 的基本使用，详细使用步骤是：

1. 打开 ModScripts/config/preset.ini 文件进行配置，里面有几个配置是需要你自己填写修改的。先把 LoaderFolder 修改成你的 3dm 的 d3d11.dll 文件所在的路径，mod_name 是生成的 ini 名称，建议使用英文名称例如 Pela(佩拉)或者 Pela_v1 之类的。

2. 在角色界面使用 F8 转储文件，然后用小键盘 789 找到角色对应的 IB，打开刚才的配置文件继续修改，把找到的 IB 填入 draw_ib，把 OutputFolder 修改成你想导出 txt 模型的路径，然后把 FrameAnalyseFolder 修改成 F8 生成的转储文件夹名称。

3. 在 ModScripts 文件夹内打开 cmd 或者 powershell(shift+右键菜单有在此打开 powershell)，执行第一个脚本：

   ```
   python ./Step1_Merge.py
   ```

   成功执行后会提取相应数据，生成贴图和 txt 模型到刚才设定的 OutputFolder 路径下，执行失败请检查配置、查看报错。

4. 将 txt 模型导入到 blender 中，进行修改，然后使用选项：3DMigoto raw buffers (.vb+.ib)进行导出，注意导出到刚才配置的output文件夹下，建议使用 txt 的名字进行命名，例如 body_part0，有多个部位则需要分别导出多次，注意名称要对应。

5. 执行第二个脚本：

   ```
   python ./Step2_Split.py
   ```

   执行成功后会生成 buf 文件。

   接着执行第三个脚本：

  ```
   python ./Step3_Generate.py
  ```

  执行成功后会生成 ini 文件。

6. 打开 3dm 所在的 Mods 文件夹，新建一个 output 文件夹，把刚才生成的 ib 和 3 个 buf 文件放进来，

   ```
   python ./Step3_Generate.py
   ```

   执行成功后会生成 ini 文件。

   进入游戏查看效果，如果你的模型炸了，再添加一个 ini 文件，内容是：

   ```ini
   [ShaderOverride_VS_动作渲染]
   hash = e8425f64cfb887cd
   if $costume_mods
     checktextureoverride = vb0
     checktextureoverride = vb3
     checktextureoverride = vb2
   endif

   [ShaderOverride_VS_贴图层渲染]
   hash = 01b83059ad73cf7e
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
     checktextureoverride = vb3
   endif

   [ShaderOverride_VS_建模层渲染]
   hash = f9f7dab05724ddee
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
   endif

   [ShaderOverride_VS_近距离渲染]
   hash = e9a6129709be6d72
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
     checktextureoverride = vb3
   endif

   [ShaderOverride_VS_近距离渲染2]
   hash = 324dbfe31f734cd9
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
     checktextureoverride = vb3
   endif

   [ShaderOverride_VS_超近距离渲染3]
   hash = 8b68e47b3572a34b
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
     checktextureoverride = vb3
   endif

   [ShaderOverride_VS_角色界面光影渲染]
   hash = 1d8ee5a4ff9f7806
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
     checktextureoverride = vb3
   endif

   [ShaderOverride_VS_角色界面光影渲染2]
   hash = dd6c633da5c62ab8
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
     checktextureoverride = vb3
   endif

   [ShaderOverride_VS_角色界面光影渲染3]
   hash = f215b617d80ca092
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
     checktextureoverride = vb3
   endif

   [ShaderOverride_VS_角色界面光影渲染4]
   hash = faa491cc37d667f3
   if $costume_mods
     checktextureoverride = ib
     checktextureoverride = vb1
     checktextureoverride = vb3
   endif
   ```

### 修改贴图

参照GIMI的贴图进行修改与配置ini，有些贴图需要自行使用 collect 脚本收集。
