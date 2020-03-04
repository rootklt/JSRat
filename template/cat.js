fso1 = new ActiveXObject("Scripting.FileSystemObject");
f = fso1.OpenTextFile("~FILENAME~", 1);
d = f.ReadAll();
f.Close();
c = "~JOB_ID~" + "|" + d;