#!/usr/bin/env python3
import requests
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Konfigurasi
DEFAULT_GITHUB_URL = (
    "https://raw.githubusercontent.com/vapaxemu/cli/refs/heads/main/worker.js"
)
API_URL = "https://api.cflifetime.workers.dev/"
ACCOUNTS_FILE = Path.cwd() / "accounts.json"
GITHUB_URLS_FILE = Path.cwd() / "github_urls.json"


class CFWorkerCLI:
    def __init__(self):
        self.accounts = self.load_accounts()
        self.github_urls = self.load_github_urls()

    def clear_screen(self):
        """Clear screen berdasarkan OS"""
        os.system("cls" if os.name == "nt" else "clear")

    def wait_enter(self):
        """Tunggu tekan enter"""
        input("\n⏎ Press Enter to continue...")

    def load_accounts(self) -> List[Dict]:
        """Load accounts dari file"""
        try:
            if ACCOUNTS_FILE.exists():
                with open(ACCOUNTS_FILE, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading accounts: {e}")
        return []

    def load_github_urls(self) -> List[Dict]:
        """Load GitHub URLs dari file"""
        try:
            if GITHUB_URLS_FILE.exists():
                with open(GITHUB_URLS_FILE, "r") as f:
                    data = json.load(f)
                    return data
            else:
                # Buat file default jika tidak ada
                default_urls = [
                    {
                        "name": "Default Worker",
                        "url": DEFAULT_GITHUB_URL,
                        "is_default": True,
                    }
                ]
                self.save_github_urls(default_urls)
                return default_urls
        except Exception as e:
            print(f"Error loading GitHub URLs: {e}")
            return []

    def save_accounts(self):
        """Simpan accounts ke file"""
        try:
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(self.accounts, f, indent=2)
        except Exception as e:
            print(f"Error saving accounts: {e}")

    def save_github_urls(self, urls=None):
        """Simpan GitHub URLs ke file"""
        try:
            if urls is None:
                urls = self.github_urls
            with open(GITHUB_URLS_FILE, "w") as f:
                json.dump(urls, f, indent=2)
        except Exception as e:
            print(f"Error saving GitHub URLs: {e}")

    def get_default_github_url(self) -> str:
        """Dapatkan default GitHub URL"""
        for item in self.github_urls:
            if item.get("is_default", False):
                return item["url"]
        # Fallback ke pertama atau default
        if self.github_urls:
            return self.github_urls[0]["url"]
        return DEFAULT_GITHUB_URL

    def set_default_github_url(self, url: str):
        """Set default GitHub URL"""
        for item in self.github_urls:
            item["is_default"] = item["url"] == url
        self.save_github_urls()

    def print_colored(self, text, color_code):
        """Print text dengan warna"""
        text = text.center(53)
        print(f"\033[{color_code}m{text}\033[0m")

    def show_success(self, message):
        self.print_colored(f"✅ {message}", "92")  # Green

    def show_error(self, message):
        self.print_colored(f"❌ {message}", "91")  # Red

    def show_warning(self, message):
        self.print_colored(f"⚠️ {message}", "93")  # Yellow

    def show_info(self, message):
        self.print_colored(f"💡 {message}", "94")  # Blue

    def show_header(
        self, title="CF Worker CLI", subtitle="Cloudflare Worker Deployment Tool"
    ):
        """Tampilkan header aplikasi"""
        self.clear_screen()
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.print_colored(f"🚀 {title}", "96")
        if subtitle:
            self.print_colored(f"{subtitle}", "93")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

    def deploy_worker(self, account: Dict, worker_name: str, github_url: str) -> Dict:
        """Deploy worker ke Cloudflare"""
        try:
            print(f"🔄 Deploying {worker_name}...")

            # Prepare request data
            request_data = {
                "email": account["email"],
                "globalAPIKey": account["global_api_key"],
                "workerName": worker_name,
                "githubUrl": github_url,
            }

            response = requests.post(API_URL, json=request_data, timeout=30)

            if response.status_code == 200:
                result_data = response.json()

                if result_data.get("success"):
                    self.show_success("Worker deployed successfully!")
                    return {"success": True, "data": result_data}
                else:
                    error_msg = result_data.get("error", "Unknown error")
                    raise Exception(f"Deployment failed: {error_msg}")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            self.show_error(f"Deployment failed: {str(e)}")
            return {"success": False, "error": str(e)}

    def display_result(self, result_data: Dict):
        """Tampilkan hasil deployment"""
        self.clear_screen()
        self.show_header("DEPLOYMENT RESULT", "Worker Successfully Deployed")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.print_colored("🎉 DEPLOYMENT SUCCESSFUL", "92")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Subscription Link
        if "sub" in result_data and result_data["sub"]:
            print("\n📋 SUBSCRIPTION LINK")
            print("🔗 " + result_data["sub"])

        # VLESS
        if "vless" in result_data and result_data["vless"]:
            print("\n🔰 VLESS CONFIG")
            print("🔗 " + result_data["vless"])

            # Extract UUID untuk info
            try:
                vless_url = result_data["vless"]
                if "vless://" in vless_url:
                    uuid_start = vless_url.find("vless://") + 8
                    uuid_end = vless_url.find("@", uuid_start)
                    if uuid_end != -1:
                        uuid = vless_url[uuid_start:uuid_end]
                        print(f"🔑 UUID: {uuid}")
            except:
                pass

        # Trojan
        if "trojan" in result_data and result_data["trojan"]:
            print("\n⚡ TROJAN CONFIG")
            print("🔗 " + result_data["trojan"])

            # Extract Password untuk info
            try:
                trojan_url = result_data["trojan"]
                if "trojan://" in trojan_url:
                    pwd_start = trojan_url.find("trojan://") + 9
                    pwd_end = trojan_url.find("@", pwd_start)
                    if pwd_end != -1:
                        password = trojan_url[pwd_start:pwd_end]
                        print(f"🔑 Password: {password}")
            except:
                pass

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.print_colored("💡 Copy URLs above and use in your client apps", "93")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def add_account(self):
        """Tambah akun baru"""
        self.show_header("ADD NEW ACCOUNT", "Add Cloudflare Account Credentials")

        email = input("📧 Cloudflare Email: ").strip()
        if not email or "@" not in email:
            self.show_error("Please enter a valid email")
            self.wait_enter()
            return

        api_key = input("🔑 Global API Key: ").strip()
        if not api_key:
            self.show_error("API Key is required")
            self.wait_enter()
            return

        self.accounts.append({"email": email, "global_api_key": api_key})
        self.save_accounts()
        self.show_success(f"Account {email} added successfully!")
        self.wait_enter()

    def list_accounts(self):
        """Tampilkan daftar akun"""
        self.show_header("ACCOUNT LIST", "Registered Cloudflare Accounts")

        if not self.accounts:
            self.show_warning("No accounts found. Add an account first.")
            self.wait_enter()
            return

        print("No.  Email".ljust(40) + "API Key")
        print("─────────────────────────────────────────────────────")
        for i, account in enumerate(self.accounts, 1):
            api_key_preview = (
                account["global_api_key"][:8] + "..." + account["global_api_key"][-4:]
            )
            print(f"{i:2}.  {account['email']}".ljust(40) + api_key_preview)

        self.wait_enter()

    def remove_account(self):
        """Hapus akun"""
        self.show_header("REMOVE ACCOUNT", "Delete Cloudflare Account")

        if not self.accounts:
            self.show_warning("No accounts to remove.")
            self.wait_enter()
            return

        print("Select account to remove:")
        print("─────────────────────────────────────────────────────")
        for i, account in enumerate(self.accounts, 1):
            print(f"{i}. {account['email']}")
        print(f"{len(self.accounts) + 1}. Cancel")
        print("─────────────────────────────────────────────────────")

        try:
            choice = int(input("\nSelect account to remove: "))
            if 1 <= choice <= len(self.accounts):
                removed_account = self.accounts.pop(choice - 1)
                self.save_accounts()
                self.show_success(
                    f"Account {removed_account['email']} removed successfully!"
                )
            else:
                self.show_info("Cancelled")
        except:
            self.show_error("Invalid choice")

        self.wait_enter()

    def add_github_url(self):
        """Tambah GitHub URL baru"""
        self.show_header("ADD GITHUB URL", "Add Custom Worker Script URL")

        name = input("📝 Script Name (e.g., 'Custom Worker v2'): ").strip()
        if not name:
            self.show_error("Script name is required")
            self.wait_enter()
            return

        url = input("🔗 GitHub URL: ").strip()
        if not url:
            self.show_error("GitHub URL is required")
            self.wait_enter()
            return

        # Cek apakah nama sudah ada
        for item in self.github_urls:
            if item["name"].lower() == name.lower():
                self.show_error(f"Script name '{name}' already exists")
                self.wait_enter()
                return

        new_item = {"name": name, "url": url, "is_default": False}

        self.github_urls.append(new_item)
        self.save_github_urls()
        self.show_success(f"GitHub URL '{name}' added successfully!")

        # Tanya apakah mau set sebagai default
        if (
            len(self.github_urls) == 1
        ):  # Jika ini URL pertama, otomatis set sebagai default
            self.set_default_github_url(url)
            self.show_info("Automatically set as default URL")
        else:
            if input("\nSet as default URL? (y/n): ").lower() == "y":
                self.set_default_github_url(url)
                self.show_success("Set as default URL!")

        self.wait_enter()

    def list_github_urls(self):
        """Tampilkan daftar GitHub URLs"""
        self.show_header("GITHUB URL LIST", "Available Worker Scripts")

        if not self.github_urls:
            self.show_warning("No GitHub URLs found. Add a URL first.")
            self.wait_enter()
            return

        print("No.  Name".ljust(30) + "URL")
        print("─────────────────────────────────────────────────────")
        for i, item in enumerate(self.github_urls, 1):
            default_indicator = " ← DEFAULT" if item.get("is_default", False) else ""
            print(f"{i:2}.  {item['name']}".ljust(30) + item["url"] + default_indicator)

        self.wait_enter()

    def remove_github_url(self):
        """Hapus GitHub URL"""
        self.show_header("REMOVE GITHUB URL", "Delete Worker Script")

        if not self.github_urls:
            self.show_warning("No GitHub URLs to remove.")
            self.wait_enter()
            return

        print("Select GitHub URL to remove:")
        print("─────────────────────────────────────────────────────")
        for i, item in enumerate(self.github_urls, 1):
            default_indicator = " (default)" if item.get("is_default", False) else ""
            print(f"{i}. {item['name']}{default_indicator}")
        print(f"{len(self.github_urls) + 1}. Cancel")
        print("─────────────────────────────────────────────────────")

        try:
            choice = int(input("\nSelect URL to remove: "))
            if 1 <= choice <= len(self.github_urls):
                removed_item = self.github_urls.pop(choice - 1)
                self.save_github_urls()
                self.show_success(
                    f"GitHub URL '{removed_item['name']}' removed successfully!"
                )

                # Jika yang dihapus adalah default, set ulang default
                if removed_item.get("is_default", False) and self.github_urls:
                    self.set_default_github_url(self.github_urls[0]["url"])
                    self.show_info(f"Default URL set to: {self.github_urls[0]['name']}")
            else:
                self.show_info("Cancelled")
        except:
            self.show_error("Invalid choice")

        self.wait_enter()

    def set_default_github_url_menu(self):
        """Set default GitHub URL"""
        self.show_header("SET DEFAULT GITHUB URL", "Choose Default Worker Script")

        if not self.github_urls:
            self.show_warning("No GitHub URLs found. Add a URL first.")
            self.wait_enter()
            return

        print("Select default GitHub URL:")
        print("─────────────────────────────────────────────────────")
        for i, item in enumerate(self.github_urls, 1):
            current_indicator = (
                " ← CURRENT DEFAULT" if item.get("is_default", False) else ""
            )
            print(f"{i}. {item['name']}{current_indicator}")
        print(f"{len(self.github_urls) + 1}. Cancel")
        print("─────────────────────────────────────────────────────")

        try:
            choice = int(input("\nSelect default URL: "))
            if 1 <= choice <= len(self.github_urls):
                selected_url = self.github_urls[choice - 1]["url"]
                self.set_default_github_url(selected_url)
                self.show_success(
                    f"Default GitHub URL set to: {self.github_urls[choice - 1]['name']}"
                )
            else:
                self.show_info("Cancelled")
        except:
            self.show_error("Invalid choice")

        self.wait_enter()

    def select_github_url(self):
        """Pilih GitHub URL untuk deployment"""
        if not self.github_urls:
            return self.get_default_github_url()

        print("\n📦 Select GitHub URL:")
        print("─────────────────────────────────────────────────────")
        for i, item in enumerate(self.github_urls, 1):
            default_indicator = " (default)" if item.get("is_default", False) else ""
            print(f"{i}. {item['name']}{default_indicator}")
        print("─────────────────────────────────────────────────────")

        try:
            choice = input(
                f"\nSelect URL [1-{len(self.github_urls)} or Enter for default]: "
            ).strip()
            if not choice:
                return self.get_default_github_url()

            choice = int(choice)
            if 1 <= choice <= len(self.github_urls):
                return self.github_urls[choice - 1]["url"]
            else:
                self.show_error("Invalid choice, using default")
                return self.get_default_github_url()
        except:
            self.show_error("Invalid input, using default")
            return self.get_default_github_url()

    def manage_accounts_menu(self):
        """Menu manajemen akun"""
        while True:
            self.show_header("ACCOUNT MANAGEMENT", "Manage Cloudflare Accounts")

            print("1. 📋 List Accounts")
            print("2. ➕ Add Account")
            print("3. 🗑️ Remove Account")
            print("4. 🔙 Back to Main Menu")
            print()

            try:
                choice = int(input("Select action: "))

                if choice == 1:
                    self.list_accounts()
                elif choice == 2:
                    self.add_account()
                elif choice == 3:
                    self.remove_account()
                elif choice == 4:
                    break
                else:
                    self.show_error("Invalid choice")
                    self.wait_enter()
            except:
                self.show_error("Invalid input")
                self.wait_enter()

    def manage_github_urls_menu(self):
        """Menu manajemen GitHub URLs"""
        while True:
            self.show_header("GITHUB URL MANAGEMENT", "Manage Worker Scripts")

            print("1. 📋 List GitHub URLs")
            print("2. ➕ Add GitHub URL")
            print("3. 🗑️ Remove GitHub URL")
            print("4. ⭐ Set Default URL")
            print("5. 🔙 Back to Main Menu")
            print()

            try:
                choice = int(input("Select action: "))

                if choice == 1:
                    self.list_github_urls()
                elif choice == 2:
                    self.add_github_url()
                elif choice == 3:
                    self.remove_github_url()
                elif choice == 4:
                    self.set_default_github_url_menu()
                elif choice == 5:
                    break
                else:
                    self.show_error("Invalid choice")
                    self.wait_enter()
            except:
                self.show_error("Invalid input")
                self.wait_enter()

    def single_deploy(self):
        """Deploy single worker"""
        self.show_header("SINGLE DEPLOYMENT", "Deploy Single Worker")

        if not self.accounts:
            self.show_warning("No accounts found. Please add an account first.")
            if input("\nDo you want to add an account now? (y/n): ").lower() == "y":
                self.add_account()
            if not self.accounts:
                return

        # Pilih akun
        print("Select account:")
        print("─────────────────────────────────────────────────────")
        for i, account in enumerate(self.accounts, 1):
            print(f"{i}. {account['email']}")
        print("─────────────────────────────────────────────────────")

        try:
            choice = int(input("\nSelect account: "))
            if not 1 <= choice <= len(self.accounts):
                self.show_error("Invalid choice")
                self.wait_enter()
                return

            account = self.accounts[choice - 1]

            # Input worker details
            worker_name = input("\n🔧 Worker name: ").strip()
            if not worker_name:
                self.show_error("Worker name is required")
                self.wait_enter()
                return

            # Pilih GitHub URL
            github_url = self.select_github_url()

            # Konfirmasi deployment
            self.show_header("DEPLOYMENT CONFIRMATION", "Review Deployment Details")

            print("📊 DEPLOYMENT SUMMARY")
            print("─────────────────────────────────────────────────────")
            print(f"📧 Account: {account['email']}")
            print(f"🔧 Worker: {worker_name}")
            print(f"📦 GitHub URL: {github_url}")
            print("─────────────────────────────────────────────────────")

            if input("\nProceed with deployment? (y/n): ").lower() == "y":
                result = self.deploy_worker(account, worker_name, github_url)
                if result["success"]:
                    self.display_result(result["data"])
                self.wait_enter()

        except:
            self.show_error("Invalid input")
            self.wait_enter()

    def bulk_deploy(self):
        """Bulk deployment"""
        self.show_header("BULK DEPLOYMENT", "Deploy Multiple Workers")

        if not self.accounts:
            self.show_warning("No accounts found. Please add accounts first.")
            self.wait_enter()
            return

        # Input worker names
        worker_names_input = input("🔧 Worker names (separate with comma): ").strip()
        if not worker_names_input:
            self.show_error("Please enter at least one worker name")
            self.wait_enter()
            return

        worker_names = [name.strip() for name in worker_names_input.split(",")]

        # Pilih GitHub URL
        github_url = self.select_github_url()

        # Konfirmasi
        self.show_header("BULK DEPLOYMENT CONFIRMATION", "Review Bulk Deployment")

        print("📊 BULK DEPLOYMENT SUMMARY")
        print("─────────────────────────────────────────────────────")
        print(f"🔧 Workers: {', '.join(worker_names)}")
        print(f"👥 Accounts: {len(self.accounts)} accounts")
        print(f"📦 GitHub URL: {github_url}")
        print(f"📊 Total deployments: {len(worker_names) * len(self.accounts)}")
        print("─────────────────────────────────────────────────────")

        if input("\nProceed with bulk deployment? (y/n): ").lower() != "y":
            self.show_info("Cancelled")
            self.wait_enter()
            return

        # Eksekusi bulk deployment
        results = []
        successful = 0
        failed = 0

        self.show_header("BULK DEPLOYMENT IN PROGRESS", "Deploying Workers...")

        total_deployments = len(worker_names) * len(self.accounts)
        current = 0

        for account in self.accounts:
            for worker_name in worker_names:
                current += 1
                print(
                    f"\n🔄 [{current}/{total_deployments}] Deploying {worker_name} to {account['email']}"
                )

                result = self.deploy_worker(account, worker_name, github_url)
                result["account"] = account["email"]
                result["worker"] = worker_name
                results.append(result)

                if result["success"]:
                    successful += 1
                    print("✅ Success")
                else:
                    failed += 1
                    print("❌ Failed")

        # Tampilkan summary
        self.show_header("BULK DEPLOYMENT COMPLETE", "Deployment Summary")

        print("📊 BULK DEPLOYMENT SUMMARY")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.print_colored(f"✅ Successful: {successful}", "92")
        self.print_colored(f"❌ Failed: {failed}", "91")
        self.print_colored(f"📊 Total: {total_deployments}", "94")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Tampilkan successful deployments
        if successful > 0:
            print(f"\n✅ SUCCESSFUL DEPLOYMENTS:")
            for result in results:
                if result["success"]:
                    print(f"• {result['worker']} on {result['account']}")

        # Tampilkan detail failures
        if failed > 0:
            print(f"\n❌ FAILED DEPLOYMENTS:")
            for result in results:
                if not result["success"]:
                    print(
                        f"• {result['worker']} on {result['account']}: {result['error']}"
                    )

        self.wait_enter()

    def show_status(self):
        """Tampilkan status konfigurasi"""
        self.show_header("SYSTEM STATUS", "Current Configuration Overview")

        print("📊 SYSTEM STATUS")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📁 Accounts File: {ACCOUNTS_FILE}")
        print(f"📁 GitHub URLs File: {GITHUB_URLS_FILE}")
        print(f"🔗 Default GitHub URL: {self.get_default_github_url()}")
        print(f"👥 Accounts Count: {len(self.accounts)}")
        print(f"📦 GitHub URLs Count: {len(self.github_urls)}")

        if self.accounts:
            print(f"\n📋 REGISTERED ACCOUNTS:")
            for acc in self.accounts:
                print(f"  • {acc['email']}")

        if self.github_urls:
            print(f"\n📦 GITHUB URLS:")
            for item in self.github_urls:
                default_indicator = (
                    " (default)" if item.get("is_default", False) else ""
                )
                print(f"  • {item['name']}{default_indicator}")

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.wait_enter()

    def main_menu(self):
        """Menu utama"""
        while True:
            self.show_header()

            print("Please select an option:")
            print("1. 🚀 Single Deployment")
            print("2. 📦 Bulk Deployment")
            print("3. 👥 Manage Accounts")
            print("4. 🔗 Manage GitHub URLs")
            print("5. 📊 System Status")
            print("6. ❌ Exit")
            print()

            try:
                choice = int(input("Select action (1-6): "))

                if choice == 1:
                    self.single_deploy()
                elif choice == 2:
                    self.bulk_deploy()
                elif choice == 3:
                    self.manage_accounts_menu()
                elif choice == 4:
                    self.manage_github_urls_menu()
                elif choice == 5:
                    self.show_status()
                elif choice == 6:
                    self.show_header("GOODBYE", "Thank you for using CF Worker CLI")
                    self.print_colored("👋 Thank you for using CF Worker CLI!", "92")
                    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    break
                else:
                    self.show_error("Please select option 1-6")
                    self.wait_enter()

            except ValueError:
                self.show_error("Please enter a number")
                self.wait_enter()
            except KeyboardInterrupt:
                self.show_header()
                self.show_info("Program interrupted by user")
                break


def main():
    """Main function"""
    try:
        # Check if requests is installed
        try:
            import requests
        except ImportError:
            print("❌ Error: 'requests' library not installed.")
            print("💡 Please install it with: pip install requests")
            sys.exit(1)

        cli = CFWorkerCLI()
        cli.main_menu()
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
