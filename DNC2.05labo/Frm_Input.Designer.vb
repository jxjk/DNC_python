<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Frm_Input
    Inherits System.Windows.Forms.Form

    'フォームがコンポーネントの一覧をクリーンアップするために dispose をオーバーライドします。
    <System.Diagnostics.DebuggerNonUserCode()> _
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
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.TB_Input = New System.Windows.Forms.TextBox()
        Me.SuspendLayout()
        '
        'Label1
        '
        Me.Label1.AutoSize = True
        Me.Label1.Font = New System.Drawing.Font("MS UI Gothic", 26.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.Label1.Location = New System.Drawing.Point(62, 47)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(279, 35)
        Me.Label1.TabIndex = 28
        Me.Label1.Text = "Input OperatorID"
        Me.Label1.TextAlign = System.Drawing.ContentAlignment.TopCenter
        '
        'TB_Input
        '
        Me.TB_Input.Font = New System.Drawing.Font("MS UI Gothic", 26.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(128, Byte))
        Me.TB_Input.ImeMode = System.Windows.Forms.ImeMode.Disable
        Me.TB_Input.Location = New System.Drawing.Point(42, 120)
        Me.TB_Input.Name = "TB_Input"
        Me.TB_Input.Size = New System.Drawing.Size(333, 42)
        Me.TB_Input.TabIndex = 29
        '
        'Frm_Input
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 12.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(396, 217)
        Me.Controls.Add(Me.TB_Input)
        Me.Controls.Add(Me.Label1)
        Me.Name = "Frm_Input"
        Me.Text = "Input Form"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents Label1 As System.Windows.Forms.Label
    Friend WithEvents TB_Input As System.Windows.Forms.TextBox
End Class
