Public Class Frm_Info

    Private Sub Frm_Info_Load(sender As System.Object, e As System.EventArgs) Handles MyBase.Load

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

    Private Sub Btn_close_Click(sender As System.Object, e As System.EventArgs) Handles Btn_close.Click
        Me.Close()
    End Sub

    'Frm_Info画面クローズ時のイベント
    Private Sub Frm_Info_FormClosed(sender As Object, e As FormClosedEventArgs) Handles MyBase.FormClosed
        If Frm_main.delAddContrlFlg = 1 Then
            Frm_main.delAddControls()
            Frm_main.delAddContrlFlg = 0 'フラグを元に戻す
        End If

        '▼151012 hishiki Brother機能追加　start
        If Frm_main.commuState = -1 Then

            '通信エラー発生時、一度SBrotherNcSysを再起動する必要がある。
            Dim p As System.Diagnostics.Process
            For Each p In System.Diagnostics.Process.GetProcesses()
                'メインウィンドウのタイトルに含まれているか調べる
                If 0 <= p.ProcessName.IndexOf("SBrotherNcSys") Then
                    'SBrotherNcSysのプロセスを停止
                    p.Kill()
                    Try
                        'SBrotherNcSysを最小化表示設定
                        Dim psi As New System.Diagnostics.ProcessStartInfo()
                        psi.FileName = Frm_main.SmacroBrother 'ini.csvに登録されたフルパスを指定
                        psi.WindowStyle = System.Diagnostics.ProcessWindowStyle.Minimized

                        'SBrotherNcSys起動
                        p = System.Diagnostics.Process.Start(psi)

                    Catch ex As Exception
                        Frm_main.Logger.Warn("SBrotherNcSys process restart Err")
                        Frm_main.Logger.Warn(ex.ToString)
                        Dim str1 As String = "Can not Open SmacroBrotherSys.exe"
                        Dim str2 As String = Frm_main.SmacroBrother
                        Frm_main.ShowFrmInfo(str1, str2)
                        Exit Sub
                    End Try

                End If
            Next
            'commuStateを0に戻す
            Frm_main.commuState = 0

        End If
        '▲151012 hishiki Brother機能追加　end

        Frm_main.TB_Barcode.Focus()
    End Sub
End Class