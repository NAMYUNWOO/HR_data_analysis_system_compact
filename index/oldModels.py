"""
class EmailData(models.Model):
    employeeID = models.ForeignKey(Employee,on_delete=models.PROTECT,null=False)
    employeeID_confirm = models.IntegerField(default=0)
    eval_date = models.DateTimeField()
    start_date = models.DateTimeField()

    email_day_mean_send = models.FloatField(null=True, default=0)
    email_day_var_send = models.FloatField(null=True, default=0)
    email_day_mean_receive = models.FloatField(null=True, default=0)
    email_day_var_receive = models.FloatField(null=True, default=0)

    email_month_mean_send = models.FloatField(null=True, default=0)
    email_month_var_send = models.FloatField(null=True, default=0)
    email_month_mean_receive = models.FloatField(null=True, default=0)
    email_month_var_receive = models.FloatField(null=True, default=0)

    sna_closeness = models.FloatField(null=True, default=0)
    sna_betweenness = models.FloatField(null=True, default=0)
    sna_eigenvector = models.FloatField(null=True, default=0)
    sna_indegree = models.FloatField(null=True, default=0)
    sna_outdegree = models.FloatField(null=True, default=0)

    buha_closeness = models.FloatField(null=True, default=0)
    buha_betweenness = models.FloatField(null=True, default=0)
    buha_eigenvector = models.FloatField(null=True, default=0)
    buha_indegree = models.FloatField(null=True, default=0)
    buha_outdegree = models.FloatField(null=True, default=0)

    dongryo_closeness = models.FloatField(null=True, default=0)
    dongryo_betweenness = models.FloatField(null=True, default=0)
    dongryo_eigenvector = models.FloatField(null=True, default=0)
    dongryo_indegree = models.FloatField(null=True, default=0)
    dongryo_outdegree = models.FloatField(null=True, default=0)

    sangsa_closeness = models.FloatField(null=True, default=0)
    sangsa_eigenvector = models.FloatField(null=True, default=0)
    sangsa_betweenness = models.FloatField(null=True, default=0)
    sangsa_indegree = models.FloatField(null=True, default=0)
    sangsa_outdegree = models.FloatField(null=True, default=0)


    email_between_1904_daycnt_send = models.FloatField(null=True, default=0)
    email_between_1904_mean_send = models.FloatField(null=True, default=0)
    email_between_1314_mean_send = models.FloatField(null=True, default=0)
    email_between_1718_mean_send = models.FloatField(null=True, default=0)
    email_between_0709_daycnt_send = models.FloatField(null=True, default=0)
    email_between_0709_mean_send = models.FloatField(null=True, default=0)

    email_between_1904_daycnt_receive = models.FloatField(null=True, default=0)
    email_between_1904_mean_receive = models.FloatField(null=True, default=0)
    email_between_1314_mean_receive = models.FloatField(null=True, default=0)
    email_between_1718_mean_receive = models.FloatField(null=True, default=0)
    email_between_0709_daycnt_receive = models.FloatField(null=True, default=0)
    email_between_0709_mean_receive = models.FloatField(null=True, default=0)


    class Graph_all:
        isinit = False
        g = nx.DiGraph()


    class Graph_sangsa:
        level = -1
        g = nx.DiGraph()

    class Graph_dongryo:
        level = -1
        g = nx.DiGraph()

    class Graph_buha:
        level = -1
        g = nx.DiGraph()

    graph_all = Graph_all()
    graph_dongryo = Graph_dongryo()
    graph_sangsa = Graph_sangsa()
    graph_buha = Graph_buha()



    def getGraph(self,querySet):
        emailcount = querySet.values("sendID","receiveID").annotate(weight = Count("sendID")).values("sendID","receiveID","weight")
        g = nx.DiGraph()
        for em in emailcount:
            node1 = em["sendID"]
            node2 = em["receiveID"]
            weight = em["weight"]
            g.add_edge(node1,node2,weight=weight)
        return g


    def getDiGraph_all(self,querySet):
        if self.graph_all.isinit == False:
            self.graph_all.isinit = True
            self.graph_all.g = self.getGraph(querySet)
        return self.graph_all.g

    def getDiGraph_sangsa(self,querySet,level):
        if self.graph_sangsa.level != level:
            self.graph_sangsa.level = level
            self.graph_sangsa.g = self.getGraph(querySet)
        return self.graph_sangsa.g

    def getDiGraph_buha(self,querySet,level):
        if self.graph_dongryo.level != level:
            self.graph_dongryo.level = level
            self.graph_dongryo.g = self.getGraph(querySet)
        return self.graph_dongryo.g


    def getDiGraph_dongryo(self,querySet,level):
        if self.graph_buha.level != level:
            self.graph_buha.level = level
            self.graph_buha.g = self.getGraph(querySet)
        return self.graph_buha.g


    def posco_set_email_sendJob(self):
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
        def send_mean_day():
            avg = emailCnctObj.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))["avg"]
            return avg

        def send_mean_month():
            avg = emailCnctObj.annotate(month=TruncMonth("eval_date")).values("month").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))["avg"]
            return avg

        def send_between_1904_daycount():
            daycnt = emailCnctObj.filter(Q(eval_date__hour__gte=19) | Q(eval_date__hour__lt=4)).annotate(day=TruncDay("eval_date")).values("day").distinct().count()
            return daycnt

        def send_between_1904_mean():
            avg = emailCnctObj.filter(Q(eval_date__hour__gte=19) | Q(eval_date__hour__lt=4)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))['avg']
            return avg
        def send_between_0709_daycount():
            daycnt = emailCnctObj.filter(Q(eval_date__hour__gte=7) & Q(eval_date__hour__lt=9)).annotate(day=TruncDay("eval_date")).values("day").distinct().count()
            return daycnt

        def send_between_0709_mean():
            avg = emailCnctObj.filter(Q(eval_date__hour__gte=7) & Q(eval_date__hour__lt=9)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))['avg']
            return avg

        def send_between_1314_mean():
            avg = emailCnctObj.filter(Q(eval_date__hour__gte=13) & Q(eval_date__hour__lt=14)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))['avg']
            return avg

        def send_between_1718_mean():
            avg = emailCnctObj.filter(Q(eval_date__hour__gte=17) & Q(eval_date__hour__lt=18)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))['avg']
            return avg


        def send_var_month():
            if emailCnctObj.count() == 0:
                return 0
            valList = list(emailCnctObj.annotate(month=TruncMonth("eval_date")).values("month").annotate(the_count=Count("receiveID")).values_list("the_count",flat=True))
            var_ = np.std(valList)
            return var_

        def send_var_day():
            if emailCnctObj.count() == 0:
                return 0
            valList = list(emailCnctObj.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).values_list("the_count",flat=True))
            var_ = np.std(valList)
            return var_
        self.email_day_mean_send = send_mean_day()
        self.email_day_var_send = send_var_day()
        self.email_month_mean_send = send_mean_month()
        self.email_month_var_send = send_var_month()
        self.email_between_1904_daycnt_send = send_between_1904_daycount()
        self.email_between_1904_mean_send = send_between_1904_mean()
        self.email_between_1314_mean_send = send_between_1314_mean()
        self.email_between_1718_mean_send = send_between_1718_mean()
        self.email_between_0709_daycnt_send = send_between_0709_daycount()
        self.email_between_0709_mean_send = send_between_0709_mean()



    def posco_set_email_receiveJob(self):
        emailCnctObj = EmailLog.objects.filter(Q(receiveID=self.employeeID_confirm) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
        def receive_mean_day():
            avg = emailCnctObj.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))["avg"]
            return avg

        def receive_mean_month():
            avg = emailCnctObj.annotate(month=TruncMonth("eval_date")).values("month").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))["avg"]
            return avg

        def receive_between_1904_daycount():
            daycnt = emailCnctObj.filter(Q(eval_date__hour__gte=19) | Q(eval_date__hour__lt=4)).annotate(day=TruncDay("eval_date")).values("day").distinct().count()
            return daycnt

        def receive_between_1904_mean():
            avg = emailCnctObj.filter(Q(eval_date__hour__gte=19) | Q(eval_date__hour__lt=4)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))['avg']
            return avg


        def receive_between_0709_daycount():
            daycnt = emailCnctObj.filter(Q(eval_date__hour__gte=7) & Q(eval_date__hour__lt=9)).annotate(day=TruncDay("eval_date")).values("day").distinct().count()
            return daycnt

        def receive_between_0709_mean():
            avg = emailCnctObj.filter(Q(eval_date__hour__gte=7) & Q(eval_date__hour__lt=9)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))['avg']
            return avg


        def receive_between_1314_mean():
            avg = emailCnctObj.filter(Q(eval_date__hour__gte=13) & Q(eval_date__hour__lt=14)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))['avg']
            return avg

        def receive_between_1718_mean():
            avg = emailCnctObj.filter(Q(eval_date__hour__gte=17) & Q(eval_date__hour__lt=18)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))['avg']
            return avg

        def receive_var_month():
            if emailCnctObj.count() == 0:
                return 0
            valList = list(emailCnctObj.annotate(month=TruncMonth("eval_date")).values("month").annotate(the_count=Count("receiveID")).values_list("the_count",flat=True))
            var_ = np.std(valList)
            return var_

        def receive_var_day():
            if emailCnctObj.count() == 0:
                return 0
            valList = list(emailCnctObj.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).values_list("the_count",flat=True))
            var_ = np.var(valList)
            return var_

        self.email_day_mean_receive = receive_mean_day()
        self.email_day_var_receive = receive_var_day()
        self.email_month_mean_receive = receive_mean_month()
        self.email_month_var_receive = receive_var_month()
        self.email_between_1904_daycnt_receive = receive_between_1904_daycount()
        self.email_between_1904_mean_receive = receive_between_1904_mean()
        self.email_between_1314_mean_receive = receive_between_1314_mean()
        self.email_between_1718_mean_receive = receive_between_1718_mean()
        self.email_between_0709_daycnt_receive = receive_between_0709_daycount()
        self.email_between_0709_mean_receive = receive_between_0709_mean()


    def _email_SNA_All(self):
        emailCnctObj = EmailLog.objects.filter(Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))

        if emailCnctObj.count() == 0:
            return
        g = self.getDiGraph_all(emailCnctObj)
        try:
            self.sna_closeness = nx.closeness_centrality(g,self.employeeID_confirm)
        except:
            pass

        try:
            self.sna_betweenness = nx.betweenness_centrality(g)[self.employeeID_confirm]
        except:
            pass


        try:
            self.sna_eigenvector = nx.eigenvector_centrality(g)[self.employeeID_confirm]
        except:
            pass

        self.sna_indegree = self.email_day_mean_receive
        self.sna_outdegree = self.email_day_mean_send
        print("All SNA")
        print("closeness %f, betweeness %f, eigenvector %f, indegree %f, outdegree %f "%(self.sna_closeness,self.sna_betweenness,self.sna_eigenvector,self.sna_indegree , self.sna_outdegree))
        return

        i = 50
        while True:
            try:
                node_eigVec = nx.eigenvector_centrality_numpy(g, max_iter=i)
                eigvecs = list(node_eigVec.values())
                eigval = np.std(eigvecs)
                eigmean = np.mean(eigvecs)
                self.sna_eigenvector = (node_eigVec[self.employeeID_confirm]-eigmean)/eigval
                break
            except:
                if i == 200:
                    break
                i += 10
                #print("sna eigVec iter %d"%i)


    def _email_SNA_Sangsa(self):
        empLevel = self.employeeID.level
        emailCnctObj = EmailLog.objects.filter(((Q(receiveID__level=empLevel) & Q(sendID__level__lt=empLevel)) | (Q(sendID__level=empLevel) & Q(receiveID__level__lt=empLevel)))&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return
        emailCnctObj1 = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm)& Q(receiveID__level__lt=empLevel) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        emailCnctObj2 = EmailLog.objects.filter(Q(receiveID=self.employeeID_confirm)& Q(receiveID__level__lt=empLevel) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        g = self.getDiGraph_sangsa(emailCnctObj, empLevel)

        try:
            self.sangsa_closeness = nx.closeness_centrality(g,self.employeeID_confirm)
        except:
            pass

        try:
            self.sangsa_betweenness = nx.betweenness_centrality(g)[self.employeeID_confirm]
        except:
            pass
        try:
            self.sangsa_eigenvector = nx.eigenvector_centrality(g)[self.employeeID_confirm]
        except:
            pass
        self.sangsa_indegree = emailCnctObj2.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))["avg"]
        self.sangsa_outdegree = emailCnctObj1.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))["avg"]


        print("sanga SNA")
        print("closeness %f, betweeness %f, eigenvector %f, indegree %f, outdegree %f "%(self.sangsa_closeness ,self.sangsa_betweenness ,self.sangsa_eigenvector ,self.sangsa_indegree ,self.sangsa_outdegree ))
        return
        i = 50
        while True:
            try:
                node_eigVec = nx.eigenvector_centrality_numpy(g, max_iter=i)
                eigvecs = list(node_eigVec.values())
                eigval = np.std(eigvecs)
                eigmean = np.mean(eigvecs)
                self.sangsa_eigenvector = (node_eigVec[self.employeeID_confirm]-eigmean)/eigval
                break
            except:
                if i == 200:
                    break
                i += 10
                #print("sna eigVec iter %d"%i)

    def _email_SNA_Dongryo(self):
        empLevel = self.employeeID.level
        emailCnctObj = EmailLog.objects.filter(Q(receiveID__level=empLevel) & Q(sendID__level=empLevel) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return
        emailCnctObj1 = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm) & Q(receiveID__level=empLevel) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
        emailCnctObj2 = EmailLog.objects.filter(Q(receiveID=self.employeeID_confirm) & Q(receiveID__level=empLevel) & Q(eval_date__gte=self.start_date) & Q(eval_date__lte=self.eval_date + datetime.timedelta(days=1)))
        g = self.getDiGraph_dongryo(emailCnctObj, empLevel)


        try:
            self.dongryo_closeness = nx.closeness_centrality(g,self.employeeID_confirm)
        except:
            pass
        try:
            self.dongryo_betweenness = nx.betweenness_centrality(g)[self.employeeID_confirm]
        except:
            pass
        try:
            self.dongryo_eigenvector = nx.eigenvector_centrality(g)[self.employeeID_confirm]
        except:
            pass
        self.dongryo_indegree = emailCnctObj2.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))["avg"]
        self.dongryo_outdegree = emailCnctObj1.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))["avg"]
        print("Dongryo SNA")
        print("closeness %f, betweeness %f, eigenvector %f, indegree %f, outdegree %f "%(self.dongryo_closeness,self.dongryo_betweenness,self.dongryo_eigenvector ,self.dongryo_indegree,self.dongryo_outdegree ))
        return
        i = 50
        while True:
            try:
                node_eigVec = nx.eigenvector_centrality_numpy(g, max_iter=i)
                eigvecs = list(node_eigVec.values())
                eigval = np.std(eigvecs)
                eigmean = np.mean(eigvecs)
                self.dongryo_eigenvector = (node_eigVec[self.employeeID_confirm]-eigmean)/eigval
                break
            except:
                if i == 200:
                    break
                i += 10
                #print("sna eigVec iter %d"%i)

    def _email_SNA_Buha(self):
        empLevel = self.employeeID.level
        emailCnctObj = EmailLog.objects.filter(((Q(receiveID__level=empLevel) & Q(sendID__level__gt=empLevel)) | (Q(sendID__level=empLevel) & Q(receiveID__level__gt=empLevel)))&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return
        emailCnctObj1 = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm)& Q(receiveID__level__gt=empLevel)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        emailCnctObj2 = EmailLog.objects.filter(Q(receiveID=self.employeeID_confirm)& Q(receiveID__level__gt=empLevel)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))


        g = self.getDiGraph_buha(emailCnctObj,empLevel)

        try:
            self.buha_closeness = nx.closeness_centrality(g,self.employeeID_confirm)
        except:
            pass
        try:
            self.buha_betweenness = nx.betweenness_centrality(g)[self.employeeID_confirm]
        except:
            pass
        try:
            self.buha_eigenvector = nx.eigenvector_centrality(g)[self.employeeID_confirm]
        except:
            pass
        self.buha_indegree = emailCnctObj2.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))["avg"]
        self.buha_outdegree = emailCnctObj1.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))["avg"]
        print("sanga SNA")
        print("closeness %f, betweeness %f, eigenvector %f, indegree %f, outdegree %f "%(self.buha_closeness ,self.buha_betweenness,self.buha_eigenvector,self.buha_indegree,self.buha_outdegree ))
        return
        i = 50
        while True:
            try:
                node_eigVec = nx.eigenvector_centrality_numpy(g, max_iter=i)
                eigvecs = list(node_eigVec.values())
                eigval = np.std(eigvecs)
                eigmean = np.mean(eigvecs)
                self.buha_eigenvector = (node_eigVec[self.employeeID_confirm]-eigmean)/eigval
                break
            except:
                if i == 200:
                    break
                i += 10
                #print("sna eigVec iter %d"%i)



    def _email_between_1904_mean_send(self):
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        avg = emailCnctObj.filter(Q(eval_date__hour__gte=19)|Q(eval_date__hour__lt = 4)).annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))['avg']
        if emailCnctObj.count() == 0:
            return 0
        # avg = emailCnctObj.filter(eval_date__hour__gte=19).extra(select={"day":"date( eval_date )"}).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))['avg']
        self.email_between_1904_mean_send = avg
        return self.email_between_1904_mean_send

    def _email_month_var_receive(self):
        emailCnctObj = EmailLog.objects.filter(Q(receiveID=self.employeeID_confirm)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        valList = list(emailCnctObj.annotate(month=TruncMonth("eval_date")).values("month").annotate(the_count=Count("receiveID")).values_list("the_count",flat=True))
        var_ = np.std(valList)
        self.email_month_var_receive = var_
        return self.email_month_var_receive


    def _email_day_mean_receive(self):
        emailCnctObj = EmailLog.objects.filter(Q(receiveID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date) & Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        avg = emailCnctObj.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("receiveID")).aggregate(avg=Avg("the_count"))["avg"]
        self.email_day_mean_receive = avg
        return self.email_day_mean_receive



    def _email_between_0709_daycnt_send(self):
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        daycnt = emailCnctObj.filter(Q(eval_date__hour__gte=7) & Q(eval_date__hour__lt=9)).annotate(day=TruncDay("eval_date")).values("day").distinct().count()
        self.email_between_0709_daycnt_send = daycnt
        return self.email_between_0709_daycnt_send


    def _email_between_1904_daycnt_send(self):
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        daycnt = emailCnctObj.filter(Q(eval_date__hour__gte=19) | Q(eval_date__hour__lt=4)).annotate(day=TruncDay("eval_date")).values("day").distinct().count()
        self.email_between_1904_daycnt_send = daycnt
        return self.email_between_1904_daycnt_send


    def _email_day_mean_send(self):
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        avg = emailCnctObj.annotate(day=TruncDay("eval_date")).values("day").annotate(the_count=Count("sendID")).aggregate(avg=Avg("the_count"))["avg"]
        self.email_day_mean_send = avg
        return self.email_day_mean_send


    def _sna_outdegree(self):
        self.sna_outdegree = self.email_day_mean_send
        return  self.sna_outdegree


    def _sna_closeness(self):
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        emailCnctObj = EmailLog.objects.filter(Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        g = self.getDiGraph_all(emailCnctObj)
        self.sna_closeness = nx.closeness_centrality(g,self.employeeID_confirm)
        return self.sna_closeness

    def _buha_closeness(self):
        empLevel = self.employeeID.level
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm)& Q(receiveID__level__gt=empLevel)&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        #emailCnctObj = EmailLog.objects.filter(Q(receiveID__level__gt=empLevel) & Q(eval_date__gte=self.yearbeforpoint()))
        #g = self.getDiGraph_buha(emailCnctObj,empLevel)
        emailCnctObj = EmailLog.objects.filter(((Q(receiveID__id=self.employeeID_confirm) & Q(sendID__level__gt=empLevel)) | (Q(sendID__id=self.employeeID_confirm) & Q(receiveID__level__gt=empLevel)))&Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        g = self.getGraph(emailCnctObj)
        self.buha_closeness = nx.closeness_centrality(g,self.employeeID_confirm)
        return self.buha_closeness


    def _dongryo_closeness(self):
        empLevel = self.employeeID.level
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm)& Q(receiveID__level=empLevel) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        emailCnctObj = EmailLog.objects.filter(Q(receiveID__level=empLevel) & Q(sendID__level=empLevel) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        g = self.getDiGraph_dongryo(emailCnctObj,empLevel)
        self.dongryo_closeness = nx.closeness_centrality(g,self.employeeID_confirm)
        return self.dongryo_closeness


    def _sangsa_eigenvector(self):
        # stored = Emaileigvec.objects.filter(Q(employeeID=self.employeeID)& Q(eval_date=self.eval_date))
        # if stored.count() != 0:
        #     self.sangsa_eigenvector = stored.first().eigVec
        #     return self.sangsa_eigenvector
        empLevel = self.employeeID.level
        emailCnctObj = EmailLog.objects.filter(Q(sendID=self.employeeID_confirm)& Q(receiveID__level__lt=empLevel) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        if emailCnctObj.count() == 0:
            return 0
        emailCnctObj = EmailLog.objects.filter(Q(receiveID__level__lt=empLevel) &Q(eval_date__gte = self.start_date)&Q(eval_date__lte = self.eval_date+datetime.timedelta(days=1)))
        g = self.getDiGraph_sangsa(emailCnctObj,empLevel)
        i = 50
        while True:
            try:
                node_eigVec = nx.eigenvector_centrality_numpy(g, max_iter=i)
                eigvecs = list(node_eigVec.values())
                eigval = np.std(eigvecs)
                eigmean = np.mean(eigvecs)
                self.sangsa_eigenvector = (node_eigVec[self.employeeID_confirm]-eigmean)/eigval
                break
            except:
                if i == 200:
                    break
                i += 10
                print("sna eigVec iter %d"%i)
        return self.sangsa_eigenvector


    def __str__(self):
        return str(self.employeeID_confirm) + "_at_" + str(self.eval_date)

"""