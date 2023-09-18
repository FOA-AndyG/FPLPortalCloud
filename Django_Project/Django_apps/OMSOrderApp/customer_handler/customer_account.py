from Django_apps.OMSOrderApp.customer_handler.customer_interface import CustomerInterface


class FPTEST(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "FPTEST"
        self.appToken = "f88b7a4b18ebe887ee7b3f5af1e1b8d5"
        self.appKey = "39c64b08d11e7f2dcabdead6aa461a2f"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 6


class XCH(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "XCH"
        self.appToken = "025295953b00711a985d4f1664e5b546"
        self.appKey = "d0319c7996b126d5d599704d7aa38c70"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class CIL(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "CIL"
        self.appToken = "4779f68e465bdab5c1d6211ebc84546e"
        self.appKey = "6e75264d8636374dc8aebbfbfed4ce99"
        self.storageRate = 0.398
        self.freeRentDays = 30
        self.warehouseID = 7


class APRIL(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "APRIL"
        self.appToken = "363ebd36473a2b9835ddcfede136ce90"
        self.appKey = "0a7768ff951453cd3dbe8ec02c9d4c1b"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class YPFL(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "YPFL"
        self.appToken = "d92e5520c8b61b6e12efc4d39de453a8"
        self.appKey = "f829308a473459c7ba25065ab7e775a0"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class LCPH(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "LCPH"
        self.appToken = "f97538f531ac6e79c4f6a19f364cb232"
        self.appKey = "cb8ccafa908646d0a853bbc09110aed3"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class NEXOES(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "NEXOES"
        self.appToken = "3c664476b7f06f84ddbdba8beb5fae08"
        self.appKey = "7f3ab18bc6edd491f86cc4c8d19b8aaf"
        self.storageRate = 0.259
        self.freeRentDays = 0
        self.warehouseID = 7


class FDW(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "FDW"
        self.appToken = "20a9ec68156ef1cfbfbb292f589f3dd3"
        self.appKey = "9847334825cf9221ad0699d8d72b43d0"
        self.storageRate = 0.259
        self.freeRentDays = 0
        self.warehouseID = 7


class SWEET(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "SWEET"
        self.appToken = "9fd4cb8c4204aa3e5aebceee07152e8e"
        self.appKey = "7b507439352d313eb77154e707673fe9"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class AVENCO(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "AVENCO"
        self.appToken = "753c3cde144ec84a6611036891777a29"
        self.appKey = "2fcf6cf8410880f046865bb1f10e7807"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class ACCF(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "ACCF"
        self.appToken = "64afe186eb9c686e306ec6626b727d73"
        self.appKey = "2cad0d20622b11c6a90783f10a17ea79"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class MORRI(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "MORRI"
        self.appToken = "712acf4543ef6f3f74e30deabbfc5371"
        self.appKey = "57f6545be9bdc5ef9234b39183966ef6"
        self.storageRate = 0.398
        self.freeRentDays = 60  # charge NEXOES storage
        self.warehouseID = 7


class SEBIKE(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "SEBIKE"
        self.appToken = "274bbafe66df1693bafeb238554a8177"
        self.appKey = "5c9a4fceb518fc0dc8372b4959241092"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class AAL(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "AAL"
        self.appToken = "791fecf539e42efceea0f3e26f79eb30"
        self.appKey = "471c7fc0c3f63ba3787ccf1a9c4427ab"
        self.storageRate = 0.398
        self.freeRentDays = 30
        self.warehouseID = 7


class HHCL(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "HHCL"
        self.appToken = "e9f4f7b0b64911d0400d392222ed6d2e"
        self.appKey = "b460d0cf23c079594d412eb364eea1db"
        self.storageRate = 0.4
        self.freeRentDays = 30
        self.warehouseID = 7


class HIGOLD(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "HIGOLD"
        self.appToken = "0026af238c3d3c7b6780969180af8f1a"
        self.appKey = "a7b827d75b14aec8811798de7a61002a"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class HKKD(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "HKKD"
        self.appToken = "3742b1a80b3d1065cc08cfa7890f0a0b"
        self.appKey = "15adfd16bbd97760d82f5f1bd8947b11"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class OUTS(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "OUTS"
        self.appToken = "224e0b6266f40b6985322bc01bba03b1"
        self.appKey = "8b717e9d35bbc7361b56b68255f04db3"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class ZXHT(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "ZXHT"
        self.appToken = "8e7e16048fd6ff0b046aa3f3340129e2"
        self.appKey = "f1988f5ee201e931ebab1166b3282a76"
        self.storageRate = 0.398
        self.freeRentDays = 60
        self.warehouseID = 7


class CCB(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "CCB"
        self.appToken = "f14d34108b5934351e3a10d55563eddc"
        self.appKey = "4e09550af0c12dde428228f3a4639e22"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class GREEM(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "GREEM"
        self.appToken = "c6f1cebef0cf8f90c59f4840e0c7082b"
        self.appKey = "f510c02053e3802c9f22cf6a08de6a70"
        self.storageRate = 0.259
        self.freeRentDays = 0
        self.warehouseID = 7


class KUKAEAST(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "KUKA"
        self.appToken = "499ad8597897e75b6bde7b5113d1d973"
        self.appKey = "e914b37e9242b3d94047895e9cd5b601"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 9


class KUKAWEST(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "KUKA"
        self.appToken = "499ad8597897e75b6bde7b5113d1d973"
        self.appKey = "e914b37e9242b3d94047895e9cd5b601"
        self.storageRate = 0.328
        self.freeRentDays = 0
        self.warehouseID = 7


class AMT(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "AMT"
        self.appToken = "21a19ea052fcde846164db11862988ef"
        self.appKey = "ce07188d1476095ec0f9619d505921f5"
        self.storageRate = 0.398
        self.freeRentDays = 60  # charge NEXOES storage, 这个nexoes来进行分销，与Aaron确认免仓期30天 # 根据Jason邮件，改为60天。
        self.warehouseID = 7


class SINO(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "SINO"
        self.appToken = "dd834672392cc4adc8481a0603fdd990"
        self.appKey = "89a879d87542db4a7129ef81daef5a28"
        self.storageRate = 0.398
        self.freeRentDays = 30
        self.warehouseID = 7


class JIEXI(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "JIEXI"
        self.appToken = "10eb68e7886b9cc5a2580a62659c94ea"
        self.appKey = "830f8cb0c36a25b7278b64292de41899"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class JSC(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "JSC"
        self.appToken = "d473a5f1bea7cf11aad02460958941e7"
        self.appKey = "287a84a00e347b459fde3bd6f3e8ccb0"
        self.storageRate = 0.398
        self.freeRentDays = 30
        self.warehouseID = 7


class APOUND(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "APOUND"
        self.appToken = "ceb518fb2192e5adc93539d0c603289c"
        self.appKey = "28e373ba67878f3b9cca7b0f8d5d6c80"
        self.storageRate = 0.398
        self.freeRentDays = 30  # Nexoes pay the free rent
        self.warehouseID = 7


class PLL(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "PLL"
        self.appToken = "c3740685415e95fb15d2a65c79fcaede"
        self.appKey = "f715f5f1d29366a3d1f8c9a03a4e861f"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class CHITA_WEST(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "CHITA_WEST"
        self.appToken = "27462183095e7be3b0d58105ef130ef3"
        self.appKey = "6dc52400c3ae296f3b75426300d1bca3"
        self.storageRate = 0.328
        self.freeRentDays = 0
        self.warehouseID = 7


class CHITA_EAST(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "CHITA_EAST"
        self.appToken = "27462183095e7be3b0d58105ef130ef3"
        self.appKey = "6dc52400c3ae296f3b75426300d1bca3"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 9


class MANWAH(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "MANWAH"
        self.appToken = "bcd01ad7c7ba0c66190c5b3646e786ff"
        self.appKey = "1ce88f5301d86747b202eec6d41ff404"
        self.storageRate = 0.3
        self.freeRentDays = 0
        self.warehouseID = 7


class LEISURE(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "LEISURE"
        self.appToken = "cf8bff7120d9db4d7f055729e4d3618e"
        self.appKey = "365343856173d739ce508eb54335bb6e"
        self.storageRate = 0.259
        self.freeRentDays = 0
        self.warehouseID = 8


class OASIS(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "OASIS"
        self.appToken = "888001cc2210ed2d3d85758376c1a7f4"
        self.appKey = "0be2535a74614a7cd368e65f24002d26"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class ZPAI(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "ZPAI"
        self.appToken = "a7df2d90e11023deeb0430cd8f096013"
        self.appKey = "4f45c8d5c7547672e01b31bf0ab2cc98"
        self.storageRate = 0.398
        self.freeRentDays = 30
        self.warehouseID = 7


class BYD(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "BYD"
        self.appToken = "31e283dc30c52a757dd506842566a996"
        self.appKey = "f9afb2232b39c9a629693753bd717caf"
        self.storageRate = 0.316
        self.freeRentDays = 7
        self.warehouseID = 7


class FINWHALE(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "FINWHALE"
        self.appToken = "d32a90ba59d0df0f54ed2d8e2f40b251"
        self.appKey = "c5aeb81bce16bdecf9ef4aa2f74cefb0"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class GRUPPOCA(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "GRUPPO_CA"
        self.appToken = "d11fade498a470a5e2f6becf91d7f12f"
        self.appKey = "d11fade498a470a5e2f6becf91d7f12f"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class GRUPPOTX(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "GRUPPO_TX1"
        self.appToken = "d11fade498a470a5e2f6becf91d7f12f"
        self.appKey = "d11fade498a470a5e2f6becf91d7f12f"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 11


class GRUPPOEAST(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "GRUPPO_EAST1"
        self.appToken = "d11fade498a470a5e2f6becf91d7f12f"
        self.appKey = "d11fade498a470a5e2f6becf91d7f12f"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 9


class DIHONG(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "DIHONG"
        self.appToken = "ec36e3616f881269f10bd30c9c95d0bb"
        self.appKey = "175bedbfd0c5c4c2d2fb95788e603106"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


class LINK(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "LINK"
        self.appToken = "fbe61df9568ac5ce6746b194d3c02176"
        self.appKey = "7d63ef86ba34a4c7d0ce4714a5b545b2"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


# increased rate day in 30 and 90
class ARJOIN(CustomerInterface):
    def __init__(self):
        super().__init__()
        self.customerCode = "ARJOIN"
        self.appToken = "87fe7b62a544facfc84d444a091673e2"
        self.appKey = "60a0163b2693adeeb697892f48e32c41"
        self.storageRate = 0.398
        self.freeRentDays = 0
        self.warehouseID = 7


# map the customer object to get key and token
def get_customer_object(customer_code):
    customer_map = {
        "XCH": XCH(),
        "CIL": CIL(),
        "APRIL": APRIL(),
        "YPFL": YPFL(),
        "LCPH": LCPH(),
        "NEXOES": NEXOES(),
        "FDW": FDW(),
        "SWEET": SWEET(),
        "AVENCO": AVENCO(),
        "ACCF": ACCF(),
        "MORRI": MORRI(),
        "SEBIKE": SEBIKE(),
        "AAL": AAL(),
        "HHCL": HHCL(),
        "HIGOLD": HIGOLD(),
        "HKKD": HKKD(),
        "OUTS": OUTS(),
        "ZXHT": ZXHT(),
        "GREEM": GREEM(),
        "KUKA_EAST": KUKAEAST(),
        "KUKA_WEST": KUKAWEST(),
        "SINO": SINO(),
        "JIEXI": JIEXI(),
        "JSC": JSC(),
        "APOUND": APOUND(),
        "PLL": PLL(),
        "MANWAH": MANWAH(),
        "CHITA_EAST": CHITA_EAST(),
        "CHITA_WEST": CHITA_WEST(),
        "LEISURE": LEISURE(),
        "OASIS": OASIS(),
        "ZPAI": ZPAI(),
        "BYD": BYD(),
        "FINWHALE": FINWHALE(),
        "GRUPPOCA": GRUPPOCA(),
        "GRUPPOTX": GRUPPOTX(),
        "GRUPPOEAST": GRUPPOEAST(),
        "DIHONG": DIHONG(),
        "LINK": LINK(),
        "ARJOIN": ARJOIN(),
    }
    if customer_code == "ALL":
        return customer_map
    else:
        return customer_map.get(customer_code)
