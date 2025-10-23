<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class Frm_main
    Inherits System.Windows.Forms.Form

    'フォームがコンポーネントの一覧をクリーンアップするために dispose をオーバーライドします。
    <System.Diagnostics.DebuggerNonUserCode()>
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Windows フォーム デザイナーで必要です。
    Private components As System.ComponentModel.IContainer

    'メモ: 以下のプロシージャは Windows フォーム デザイナーで必要です。
    'Windows フォーム デザイナーを使用して変更できます。  
    'コード エディターを使って変更しないでください。
    <System.Diagnostics.DebuggerStepThrough()>
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Me.TB_Model = New System.Windows.Forms.TextBox()
        Me.TB_Barcode = New System.Windows.Forms.TextBox()
        Me.TB_alart = New System.Windows.Forms.TextBox()
        Me.Timer1 = New System.Windows.Forms.Timer(Me.components)
        Me.FlowLayoutPanel3 = New System.Windows.Forms.FlowLayoutPanel()
        Me.Btn_chgOperator = New System.Windows.Forms.Button()
        Me.Btn_Keyboard = New System.Windows.Forms.Button()
        Me.Btn_send = New System.Windows.Forms.Button()
        Me.Btn_chngprgrm = New System.Windows.Forms.Button()
        Me.FlowLayoutPanel1 = New System.Windows.Forms.FlowLayoutPanel()
        Me.Panel1 = New System.Windows.Forms.Panel()
        Me.FlowLayoutPanel2 = New System.Windows.Forms.FlowLayoutPanel()
        Me.TB_Prg = New System.Windows.Forms.TextBox()
        Me.TB_OpeID = New System.Windows.Forms.TextBox()
        Me.CB_Connection = New System.Windows.Forms.CheckBox()
        Me.FlowLayoutPanel3.SuspendLayout()
        Me.FlowLayoutPanel1.SuspendLayout()
        Me.FlowLayoutPanel2.SuspendLayout()
        Me.SuspendLayout()
        '
        'TB_Model
        '
        Me.TB_Model.BackColor = System.Drawing.Color.White
        Me.TB_Model.CausesValidation = False
        Me.TB_Model.Font = New System.Drawing.Font("MS UI Gothic", 26.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.TB_Model.ForeColor = System.Drawing.SystemColors.InfoText
        Me.TB_Model.Location = New System.Drawing.Point(5, 4)
        Me.TB_Model.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.TB_Model.Name = "TB_Model"
        Me.TB_Model.ReadOnly = True
        Me.TB_Model.Size = New System.Drawing.Size(1302, 60)
        Me.TB_Model.TabIndex = 12
        '
        'TB_Barcode
        '
        Me.TB_Barcode.Font = New System.Drawing.Font("MS UI Gothic", 26.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.TB_Barcode.ImeMode = System.Windows.Forms.ImeMode.Disable
        Me.TB_Barcode.Location = New System.Drawing.Point(5, 4)
        Me.TB_Barcode.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.TB_Barcode.Name = "TB_Barcode"
        Me.TB_Barcode.Size = New System.Drawing.Size(1251, 60)
        Me.TB_Barcode.TabIndex = 14
        '
        'TB_alart
        '
        Me.TB_alart.Cursor = System.Windows.Forms.Cursors.No
        Me.TB_alart.Font = New System.Drawing.Font("ＭＳ ゴシック", 36.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.TB_alart.ForeColor = System.Drawing.Color.Red
        Me.TB_alart.Location = New System.Drawing.Point(492, 416)
        Me.TB_alart.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.TB_alart.Name = "TB_alart"
        Me.TB_alart.Size = New System.Drawing.Size(1187, 79)
        Me.TB_alart.TabIndex = 29
        Me.TB_alart.Text = "数据转送后，5秒钟内不能变更"
        Me.TB_alart.TextAlign = System.Windows.Forms.HorizontalAlignment.Center
        '
        'Timer1
        '
        Me.Timer1.Interval = 500
        '
        'FlowLayoutPanel3
        '
        Me.FlowLayoutPanel3.Controls.Add(Me.TB_Barcode)
        Me.FlowLayoutPanel3.Controls.Add(Me.Btn_chgOperator)
        Me.FlowLayoutPanel3.Controls.Add(Me.Btn_Keyboard)
        Me.FlowLayoutPanel3.Controls.Add(Me.Btn_send)
        Me.FlowLayoutPanel3.Location = New System.Drawing.Point(32, 826)
        Me.FlowLayoutPanel3.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.FlowLayoutPanel3.Name = "FlowLayoutPanel3"
        Me.FlowLayoutPanel3.Size = New System.Drawing.Size(1932, 87)
        Me.FlowLayoutPanel3.TabIndex = 30
        '
        'Btn_chgOperator
        '
        Me.Btn_chgOperator.Font = New System.Drawing.Font("MS UI Gothic", 15.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.Btn_chgOperator.Location = New System.Drawing.Point(1266, 4)
        Me.Btn_chgOperator.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.Btn_chgOperator.Name = "Btn_chgOperator"
        Me.Btn_chgOperator.Size = New System.Drawing.Size(208, 74)
        Me.Btn_chgOperator.TabIndex = 18
        Me.Btn_chgOperator.Text = "Operator"
        Me.Btn_chgOperator.UseVisualStyleBackColor = True
        '
        'Btn_Keyboard
        '
        Me.Btn_Keyboard.Font = New System.Drawing.Font("MS UI Gothic", 15.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.Btn_Keyboard.Location = New System.Drawing.Point(1484, 4)
        Me.Btn_Keyboard.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.Btn_Keyboard.Name = "Btn_Keyboard"
        Me.Btn_Keyboard.Size = New System.Drawing.Size(208, 74)
        Me.Btn_Keyboard.TabIndex = 15
        Me.Btn_Keyboard.Text = "KeyBoard"
        Me.Btn_Keyboard.UseVisualStyleBackColor = True
        '
        'Btn_send
        '
        Me.Btn_send.Font = New System.Drawing.Font("MS UI Gothic", 15.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.Btn_send.Location = New System.Drawing.Point(1702, 4)
        Me.Btn_send.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.Btn_send.Name = "Btn_send"
        Me.Btn_send.Size = New System.Drawing.Size(208, 74)
        Me.Btn_send.TabIndex = 17
        Me.Btn_send.Text = "转让"
        Me.Btn_send.UseVisualStyleBackColor = True
        '
        'Btn_chngprgrm
        '
        Me.Btn_chngprgrm.Font = New System.Drawing.Font("MS UI Gothic", 15.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.Btn_chngprgrm.Location = New System.Drawing.Point(1317, 4)
        Me.Btn_chngprgrm.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.Btn_chngprgrm.Name = "Btn_chngprgrm"
        Me.Btn_chngprgrm.Size = New System.Drawing.Size(208, 69)
        Me.Btn_chngprgrm.TabIndex = 13
        Me.Btn_chngprgrm.Text = "Button1"
        Me.Btn_chngprgrm.UseVisualStyleBackColor = True
        '
        'FlowLayoutPanel1
        '
        Me.FlowLayoutPanel1.AutoScroll = True
        Me.FlowLayoutPanel1.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle
        Me.FlowLayoutPanel1.Controls.Add(Me.Panel1)
        Me.FlowLayoutPanel1.FlowDirection = System.Windows.Forms.FlowDirection.TopDown
        Me.FlowLayoutPanel1.ImeMode = System.Windows.Forms.ImeMode.Alpha
        Me.FlowLayoutPanel1.Location = New System.Drawing.Point(42, 96)
        Me.FlowLayoutPanel1.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.FlowLayoutPanel1.Name = "FlowLayoutPanel1"
        Me.FlowLayoutPanel1.Size = New System.Drawing.Size(1879, 720)
        Me.FlowLayoutPanel1.TabIndex = 28
        '
        'Panel1
        '
        Me.Panel1.Location = New System.Drawing.Point(5, 4)
        Me.Panel1.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.Panel1.Name = "Panel1"
        Me.Panel1.Size = New System.Drawing.Size(222, 100)
        Me.Panel1.TabIndex = 0
        '
        'FlowLayoutPanel2
        '
        Me.FlowLayoutPanel2.Controls.Add(Me.TB_Model)
        Me.FlowLayoutPanel2.Controls.Add(Me.Btn_chngprgrm)
        Me.FlowLayoutPanel2.Controls.Add(Me.TB_Prg)
        Me.FlowLayoutPanel2.Controls.Add(Me.CB_Connection)
        Me.FlowLayoutPanel2.Location = New System.Drawing.Point(27, 3)
        Me.FlowLayoutPanel2.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.FlowLayoutPanel2.Name = "FlowLayoutPanel2"
        Me.FlowLayoutPanel2.Size = New System.Drawing.Size(1928, 80)
        Me.FlowLayoutPanel2.TabIndex = 27
        '
        'TB_Prg
        '
        Me.TB_Prg.Font = New System.Drawing.Font("MS UI Gothic", 26.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.TB_Prg.Location = New System.Drawing.Point(1535, 4)
        Me.TB_Prg.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.TB_Prg.Name = "TB_Prg"
        Me.TB_Prg.Size = New System.Drawing.Size(264, 60)
        Me.TB_Prg.TabIndex = 18
        '
        'TB_OpeID
        '
        Me.TB_OpeID.Font = New System.Drawing.Font("MS UI Gothic", 26.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.TB_OpeID.Location = New System.Drawing.Point(1772, 416)
        Me.TB_OpeID.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.TB_OpeID.Name = "TB_OpeID"
        Me.TB_OpeID.Size = New System.Drawing.Size(109, 60)
        Me.TB_OpeID.TabIndex = 31
        '
        'CB_Connection
        '
        Me.CB_Connection.AutoSize = True
        Me.CB_Connection.Font = New System.Drawing.Font("MS UI Gothic", 14.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.CB_Connection.Location = New System.Drawing.Point(1807, 3)
        Me.CB_Connection.Name = "CB_Connection"
        Me.CB_Connection.Size = New System.Drawing.Size(96, 32)
        Me.CB_Connection.TabIndex = 32
        Me.CB_Connection.Text = "接続"
        Me.CB_Connection.UseVisualStyleBackColor = True
        '
        'Frm_main
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(10.0!, 18.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(2000, 916)
        Me.Controls.Add(Me.TB_alart)
        Me.Controls.Add(Me.FlowLayoutPanel3)
        Me.Controls.Add(Me.FlowLayoutPanel1)
        Me.Controls.Add(Me.FlowLayoutPanel2)
        Me.Controls.Add(Me.TB_OpeID)
        Me.Margin = New System.Windows.Forms.Padding(5, 4, 5, 4)
        Me.Name = "Frm_main"
        Me.Text = "DNC"
        Me.FlowLayoutPanel3.ResumeLayout(False)
        Me.FlowLayoutPanel3.PerformLayout()
        Me.FlowLayoutPanel1.ResumeLayout(False)
        Me.FlowLayoutPanel2.ResumeLayout(False)
        Me.FlowLayoutPanel2.PerformLayout()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents TB_Model As System.Windows.Forms.TextBox
    Friend WithEvents TB_Barcode As System.Windows.Forms.TextBox
    Friend WithEvents TB_alart As System.Windows.Forms.TextBox
    Friend WithEvents Timer1 As System.Windows.Forms.Timer
    Friend WithEvents FlowLayoutPanel3 As System.Windows.Forms.FlowLayoutPanel
    Friend WithEvents Btn_Keyboard As System.Windows.Forms.Button
    Friend WithEvents Btn_send As System.Windows.Forms.Button
    Friend WithEvents Btn_chngprgrm As System.Windows.Forms.Button
    Friend WithEvents FlowLayoutPanel1 As System.Windows.Forms.FlowLayoutPanel
    Friend WithEvents FlowLayoutPanel2 As System.Windows.Forms.FlowLayoutPanel
    Friend WithEvents TB_Prg As System.Windows.Forms.TextBox
    Friend WithEvents Btn_chgOperator As System.Windows.Forms.Button
    Friend WithEvents TB_OpeID As System.Windows.Forms.TextBox
    Friend WithEvents Panel1 As System.Windows.Forms.Panel
    Friend WithEvents CB_Connection As CheckBox
End Class
