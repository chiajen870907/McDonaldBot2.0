from module.mcd.McDonald import McDonald as md

class MCDHelper():
    def __int__(self):
        self.account = None

    def connect(self,token):
        self.account = md(token)

    def get_sircketlist(self,token):
        self.connect(token)
        return self.account.Sticker_List()

    def get_couponlist(self,token):
        self.connect(token)
        return self.account.Coupon_List()

    def get_lottery(self,token):
        self.connect(token)
        return self.account.Lottery()

    def get_stickers_lottery(self,token):
        self.connect(token)
        return self.account.Sticker_lottery()



