Imports System.Runtime.InteropServices

'2015/08/31 ins tsukiji 日報監視、無操作時間が経過後、DNCをアクティブにする。
Public Class clsFormFocus

    Private Const checkTitle As String = "Daily Report"
    Private Const C_SEP As String = "-"     'タイトルと経過時間の区分け文字列 

    '現在アクティブのウィンドウハンドル取得
    <DllImport("user32.dll")> _
    Private Shared Function GetForegroundWindow() As IntPtr
    End Function

    '戻り値
    'false: 既存の動作でDNCを前に。   ( 経過時間が未経過でDRも非アクティブ 、DR起動なし)
    'true : DRはアクティブのまま。既存動作不要    ( 経過時間が未経過でDRがアクティブ )
    'true : DNCをアクティブ済み。既存動作不要     ( 時間経過してDNCをアクティブにした )
    Public Function execFormFocus(ByVal iSpanTime As Integer) As Boolean

        'title想定
        ' Daily Report Login - 13 - Internet Explorer
        ' Daily Report Login - 13 - <お気に入りの名前>
        ' Daily Report Login - 13 - Google Chrome
        ' この13を13secとして切り出す。

        'メイン画面以外に、サブ画面がある。サブ画面がアクティブの時には、メインをactive→サブをactiveとし、サブ画面がフォーカスを持つようにする。

        '経過時間は、master\ini.csvのWaitTime_TB_Focus,5,TB_Barcodeからフォーカスが外れた後、元に戻るまでの時間（sec）設定
        'にて制御する。時間はsec指定のため、5だと5secの時間と判定する。

        'すべてのプロセスを列挙する
        Dim p As System.Diagnostics.Process
        Dim sTitle As String
        Dim sTime As String
        Dim iTime As Integer
        Dim bActiveDailyReport As Boolean
        Try

            For Each p In System.Diagnostics.Process.GetProcesses()
                'メインウィンドウのタイトルに含まれているか調べる
                If 0 <= p.MainWindowTitle.IndexOf(checkTitle) Then
                    'windows 8だと変わった??
                    If p.MainWindowTitle.Trim.Length <> 0 Then
                        Frm_main.Logger.Debug("Title:" & p.MainWindowTitle)
                    End If

                    '日報がアクティブかどうか。
                    bActiveDailyReport = False  'true:使用 false:未使用
                    If p.MainWindowHandle = GetForegroundWindow() Then
                        '日報がアクティブ
                        Frm_main.Logger.Debug("DR Active")
                        bActiveDailyReport = True
                    End If

                    '日報システム タイトルの調整(経過時間読み取りのため。)
                    ' titleの文字列切り取り
                    ' title - [未処理時間] が入っている。
                    sTitle = p.MainWindowTitle
                    'sTitle = sTitle.Replace("- Internet Explorer", "")   'IE使用時の文字列を排除
                    'sTitle = sTitle.Replace("- Google Chrome", "")   'Chrome使用時の文字列を排除
                    'If sTitle.IndexOf(C_SEP) >= 0 Then

                    Dim sidx As Integer = p.MainWindowTitle.IndexOf(C_SEP)
                    Dim nidx As Integer = p.MainWindowTitle.IndexOf(C_SEP, sidx + 1)
                    If sidx >= 0 AndAlso nidx >= 0 Then
                        '区分け文字 発見　(未発見の時-1が返る)
                        'sTime = sTitle.Substring(sTitle.IndexOf(C_SEP) + 1, sTitle.Length - sTitle.IndexOf(C_SEP) - 1)
                        sTime = sTitle.Substring(sidx + 1, nidx - sidx - 1)
                        If Integer.TryParse(sTime, iTime) Then
                            '経過時間取得成功
                            If iTime > iSpanTime Then

                                'DNC 前面
                                Dim bFocus As Boolean = False

                                'main form
                                Dim fmain As Form = Application.OpenForms("Frm_main")
                                If Not IsNothing(fmain) Then
                                    If fmain.WindowState = System.Windows.Forms.FormWindowState.Minimized Then
                                        '最小化されていたらもとにもどす。
                                        fmain.WindowState = System.Windows.Forms.FormWindowState.Normal
                                    End If
                                    fmain.WindowState = System.Windows.Forms.FormWindowState.Minimized
                                    fmain.WindowState = System.Windows.Forms.FormWindowState.Normal
                                    bFocus = True
                                End If
                                'sub form
                                For Each fapp As Form In Application.OpenForms
                                    If fapp.Name <> "Frm_main" Then
                                        If fapp.WindowState = System.Windows.Forms.FormWindowState.Minimized Then
                                            '最小化されていたら
                                            fapp.WindowState = System.Windows.Forms.FormWindowState.Normal
                                        End If
                                        fapp.WindowState = System.Windows.Forms.FormWindowState.Minimized
                                        fapp.WindowState = System.Windows.Forms.FormWindowState.Normal
                                        bFocus = True
                                    End If
                                Next
                                If bFocus = True Then
                                    Return True '既存動作不要
                                End If
                            Else
                                '時間未経過
                                Frm_main.Logger.Debug("DR Time [" & iTime.ToString() & "]")
                                If bActiveDailyReport Then
                                    '日報がActive
                                    Return True '既存動作不要
                                End If
                            End If
                        Else
                            Frm_main.Logger.Debug("DR Time get failure [" & sTime & "]")
                            'Add Start 15/09/03 H.Kimura
                            If bActiveDailyReport Then
                                '日報がActive
                                Return True '既存動作不要
                            End If
                            'Add End   15/09/03 H.Kimura
                        End If

                    Else
                        '日報の画面の切り替わりの瞬間にここにきて、DNCが前に出てしまう。
                        Frm_main.Logger.Debug("DR title not found separate charactor [" & sTitle & "]")
                        If bActiveDailyReport Then
                            '日報がActive
                            Return True '既存動作不要
                        End If

                    End If

                End If

            Next

            Return False

        Catch ex As Exception
            'Add Start 15/09/03 H.Kimura
            Frm_main.Logger.Error(ex.ToString())
            'Add End   15/09/03 H.Kimura
            Return False

        End Try
    End Function

End Class
