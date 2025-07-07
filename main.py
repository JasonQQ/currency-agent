from currency_agent import CurrencyAgent

if __name__ == "__main__":
    agent = CurrencyAgent()
    print("欢迎使用货币转换和汇率查询 Agent！请输入您的问题（如：USD 转换为 JPY，或 美元对日元汇率）：")
    while True:
        user_input = input("用户: ")
        if user_input.strip().lower() in ("exit", "quit", "q"):  # 退出指令
            print("再见！")
            break
        for resp in agent.stream(user_input):
            print(f"Agent: {resp}") 