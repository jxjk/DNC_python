Public Class Frm_Input
    Private Sub Frm_Input_Load(sender As System.Object, e As System.EventArgs) Handles MyBase.Load

        '150901 hishiki main以外の画面（keyboard,input,info）の表示位置変更 -start-
        ''フォームをメインフォームの中央に配置
        'Dim bufX, bufY As Integer
        'bufX = Frm_main.Location.X + (Frm_main.Width - Me.Width) / 2
        'bufY = Frm_main.Location.Y + (Frm_main.Height - Me.Height) / 2
        'Me.Location = New Point(bufX, bufY)

        'フォームをディスプレイの中央に配置
        'ディスプレイの幅
        Dim w As Integer = System.Windows.Forms.Screen.PrimaryScreen.Bounds.Width
        'ディスプレイの高さ
        Dim h As Integer = System.Windows.Forms.Screen.PrimaryScreen.Bounds.Height

        Dim bufX, bufY As Integer
        bufX = (w - Me.Width) / 2
        bufY = (h - Me.Height) / 2
        Me.Location = New Point(bufX, bufY)
        '150901 hishiki main以外の画面（keyboard,input,info）の表示位置変更 -end-

    End Sub
    Private Sub TB_Input_KeyDown(sender As System.Object, e As System.Windows.Forms.KeyEventArgs) Handles TB_Input.KeyDown
        If (e.KeyCode = Keys.Enter) Then
            Frm_main.TB_OpeID.Text = TB_Input.Text
            Me.Close()
        End If

    End Sub

    Private Sub Frm_Input_FormClosed(sender As Object, e As FormClosedEventArgs) Handles MyBase.FormClosed
        Frm_main.TB_Barcode.Focus()
    End Sub
End Class